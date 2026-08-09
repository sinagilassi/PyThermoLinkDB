# import packages/modules
from examples.sources.source_2 import (
    butyl_methyl_ether,
    ethanol,
    methanol,
    model_source,
)
from rich import print
from pythermodb_settings.utils import create_mixture_id
from pyThermoLinkDB import MatrixDataSourcesCore, mkmdts
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb
import numpy as np
import os
import sys

# NOTE: allow running this file directly from examples/mks
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


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
mixture_key = 'Name'

mixture_components = [methanol, ethanol, butyl_methyl_ether]

matrix_data_source: MatrixDataSourcesCore | None = mkmdts(
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
# DICTIONARY KEYS
# =======================================
mixture_id = create_mixture_id(
    components=mixture_components,
    mixture_key=mixture_key,
)

print(mixture_id)
print(matrix_data_source.mixture_name)
print(matrix_data_source.component_names)

# ! build status
print(matrix_data_source.summary())
print(matrix_data_source.build_status())

# ! all matrix properties
print(matrix_data_source.props)
print(matrix_data_source.all_props())
print(matrix_data_source.props_symbols)

# ! available properties
print(matrix_data_source.is_prop_available('alpha'))
print(matrix_data_source.is_prop_available('unknown_matrix_property'))

# ! check a list of matrix properties
print(matrix_data_source.check_availability(['alpha', 'b']))
print(matrix_data_source.all_available(['alpha']))

# ! specific matrix property
alpha_data = matrix_data_source.get_matrix(name='alpha')
print(type(alpha_data))
print(alpha_data)

# =======================================
# MATRIX TABLES AND LOOKUPS
# =======================================
# ! alpha
print("=== ALPHA MATRIX ===")
print(matrix_data_source.table(name='alpha', mode='selected'))
print(matrix_data_source.structure(name='alpha'))

print(matrix_data_source.ij(
    name='alpha',
    property='alpha | methanol | ethanol',
))

print(matrix_data_source.matrix_property(
    name='alpha',
    property='alpha_i_j',
    component_names=['methanol', 'ethanol'],
))

# ! b
print("=== B MATRIX ===")
print(matrix_data_source.table(name='b', mode='selected'))
print(matrix_data_source.structure(name='b'))

print(matrix_data_source.ij(
    name='b',
    property='b | methanol | ethanol',
))

print(matrix_data_source.matrix_property(
    name='b',
    property='b_i_j',
    component_names=['methanol', 'ethanol'],
))

# =======================================
# MATRIX BUILDERS
# =======================================
alpha_matrix = matrix_data_source.mat(
    name='alpha',
    symbol_format='numeric',
    component_key='Name',
)
print(alpha_matrix)

if isinstance(alpha_matrix, np.ndarray):
    print(f"alpha matrix shape: {alpha_matrix.shape}")

print(matrix_data_source.mat(
    name='alpha',
    symbol_format='alphabetic',
    component_key='Name',
))

print(matrix_data_source.matX(
    name='alpha',
    components=mixture_components,
    symbol_format='numeric',
    component_key='Name',
))
