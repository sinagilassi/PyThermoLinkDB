import os
import sys

# NOTE: allow running this file directly from examples/mks
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# import packages/modules
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from examples.sources.source_2 import (
    butyl_methyl_ether,
    ethanol,
    methanol,
    model_source,
)
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
# MAKE ONE MATRIX DATA SOURCE DIRECTLY
# =======================================
mixture_key: MixtureKey = 'Name'
mixture_components = [methanol, ethanol, butyl_methyl_ether]

matrix_data_source: MatrixDataSourceCore | None = mkmdt(
    name='alpha',
    components=mixture_components,
    model_source=model_source,
    mixture_key=mixture_key,
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

print(matrix_data_source.is_prop_available())

# =======================================
# RAW MATRIX DATA
# =======================================
alpha_data = matrix_data_source.prop()
print(type(alpha_data))
print(alpha_data)

print(matrix_data_source.table(mode='selected'))
print(matrix_data_source.structure())

# =======================================
# MATRIX LOOKUPS
# =======================================
print(matrix_data_source.ij(
    property='alpha | methanol | ethanol',
))

print(matrix_data_source.matrix_property(
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
