# import packages/modules
import os
import sys

# NOTE: allow running this file directly from examples/mks
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from examples.sources.source_2 import (
    butyl_methyl_ether,
    ethanol,
    methanol,
    components,
    model_source,
)

import numpy as np
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import MatrixDataSourceCore, mkmdt
from pythermodb_settings.models import MixtureKey
from pythermodb_settings.utils import create_mixture_id
from rich import print

# ! model source & components


# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# MODEL SOURCE
# =======================================
datasource = model_source.data_source
equationsource = model_source.equation_source

print(datasource.keys())
print(equationsource.keys())

# =======================================
# MAKE MATRIX DATA SOURCE DIRECTLY
# =======================================
mixture_key: MixtureKey = 'Name'
mixture_components = [methanol, ethanol, butyl_methyl_ether]

matrix_data_source: MatrixDataSourceCore | None = mkmdt(
    components=mixture_components,
    model_source=model_source,
    mixture_key=mixture_key,
    extract_list=['alpha', 'b'],
)

print(matrix_data_source)

# >> check
if matrix_data_source is None:
    raise ValueError("Failed to create matrix data source.")

# =======================================
# GENERATED MIXTURE ID
# =======================================
mixture_id = create_mixture_id(
    components=mixture_components,
    mixture_key=mixture_key,
)

print(mixture_id)
print(matrix_data_source.mixture_name)

# =======================================
# BUILD STATUS
# =======================================
print(matrix_data_source.summary())
print(matrix_data_source.build_status())

# =======================================
# AVAILABLE MATRIX PROPERTIES
# =======================================
print(matrix_data_source.props)
print(matrix_data_source.all_props())
print(matrix_data_source.props_symbols)

print(matrix_data_source.is_prop_available('alpha'))
print(matrix_data_source.is_prop_available('unknown_matrix_property'))
print(matrix_data_source.check_availability(['alpha', 'b']))
print(matrix_data_source.all_available(['alpha']))

# =======================================
# RAW MATRIX DATA
# =======================================
alpha_data = matrix_data_source.prop(name='alpha')
print(type(alpha_data))
print(alpha_data)

print(matrix_data_source.table(name='alpha', mode='selected'))
print(matrix_data_source.structure(name='alpha'))

# =======================================
# MATRIX LOOKUPS
# =======================================
print(matrix_data_source.ij(
    name='alpha',
    property='alpha | methanol | ethanol',
))

print(matrix_data_source.matrix_property(
    name='alpha',
    property='alpha_i_j',
    component_names=['methanol', 'ethanol'],
))

# =======================================
# MATRIX BUILDERS
# =======================================
alpha_matrix = matrix_data_source.mat(
    name='alpha',
    symbol_format='numeric',
)
print(alpha_matrix)

print(matrix_data_source.mat(
    name='alpha',
    symbol_format='alphabetic',
    component_key='Formula',
))

print(matrix_data_source.matX(
    name='alpha',
    components=components,
    symbol_format='numeric',
))

# =======================================
# MATRIX ORDER COMPARISON
# =======================================
def show_b_matrix_order(
    title: str,
    mixture_components_ordered: list,
) -> None:
    print(f"\n[bold cyan]{title}[/bold cyan]")
    print(f"Component order: {[component.name for component in mixture_components_ordered]}")

    matrix_data_source_ordered: MatrixDataSourceCore | None = mkmdt(
        components=mixture_components_ordered,
        model_source=model_source,
        mixture_key=mixture_key,
        extract_list=['b'],
    )

    if matrix_data_source_ordered is None:
        raise ValueError("Failed to create matrix data source.")

    b_data = matrix_data_source_ordered.prop(name='b')
    if b_data is None:
        raise ValueError("Missing b matrix data.")

    component_names = [
        component.name
        for component in mixture_components_ordered
    ]

    b_matrix = b_data.mat(
        property_name='b',
        component_names=component_names,
        symbol_format='numeric',
        component_key='Name',
    )
    print("\nb matrix from mat() using component_names order:")
    print(b_matrix)

    if isinstance(b_matrix, np.ndarray):
        print(f"mat() b matrix shape: {b_matrix.shape}")

    b_matrix_x = b_data.matX(
        property_name='b',
        components=mixture_components_ordered,
        symbol_format='numeric',
        component_key='Name',
    )
    print("\nb matrix from matX() using components order:")
    print(b_matrix_x)

    if isinstance(b_matrix_x, np.ndarray):
        print(f"matX() b matrix shape: {b_matrix_x.shape}")


show_b_matrix_order(
    title='Order 1: methanol, ethanol, butyl-methyl-ether',
    mixture_components_ordered=[methanol, ethanol, butyl_methyl_ether],
)

show_b_matrix_order(
    title='Order 2: butyl-methyl-ether, ethanol, methanol',
    mixture_components_ordered=[butyl_methyl_ether, ethanol, methanol],
)
