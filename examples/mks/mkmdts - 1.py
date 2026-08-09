# import packages/modules
import os
import sys

# NOTE: allow running this file directly from examples/mks
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import MatrixDataSourceCore, MatrixDataSourcesCore, mkmdts
from pythermodb_settings.utils import create_mixture_id
from rich import print

# ! model source & components
from examples.sources.source_2 import (
    butyl_methyl_ether,
    ethanol,
    methanol,
    model_source,
)


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
# MAKE MATRIX DATA SOURCES DIRECTLY
# =======================================
mixture_key = 'Name'

mixture_components = [
    [methanol, ethanol, butyl_methyl_ether],
]

matrix_data_sources: dict[str, MatrixDataSourcesCore] | None = mkmdts(
    mixture_components=mixture_components,
    model_source=model_source,
    mixture_key=mixture_key,
    extract_list=['alpha'],
    check_build=True,
)

print(matrix_data_sources)

# >> check
if matrix_data_sources is None:
    raise ValueError("Failed to create matrix data sources.")

# =======================================
# DICTIONARY KEYS
# =======================================
mixture_ids = [
    create_mixture_id(
        components=components,
        mixture_key=mixture_key,
    )
    for components in mixture_components
]

print(mixture_ids)
print(matrix_data_sources.keys())

# =======================================
# ACCESS MATRIX DATA SOURCE
# =======================================
mixture_id = mixture_ids[0]
matrix_data_sources_core = matrix_data_sources[mixture_id]
matrix_data_source: MatrixDataSourceCore | None = matrix_data_sources_core.select(
    mixture_id=mixture_id,
)

if matrix_data_source is None:
    raise ValueError(f"Failed to select matrix data source for {mixture_id}.")

print(matrix_data_sources_core.summary())
print(matrix_data_sources_core.build_status())

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

# =======================================
# MATRIX BUILDERS
# =======================================
print(
    "Matrix builders are skipped for this ternary pair-row table; "
    "use table(), structure(), ij(), or matrix_property() for this source."
)
