# import packages/modules
import numpy as np
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoDB import (
    MixtureThermoDB,
    TableMatrixData,
    build_mixture_thermodb_from_reference,
)
from pythermodb_settings.models import Component
from rich import print

from pyThermoLinkDB import build_mixture_model_source, build_model_source
from pyThermoLinkDB.models import MixtureModelSource, ModelSource
from pyThermoLinkDB.thermo import Source

# ! version
print(ptdb.__version__)
print(ptdblink.__version__)

# ====================================================
# SECTION: REFERENCE CONTENT
# ====================================================
REFERENCE_CONTENT = """
REFERENCES:
    CUSTOM-REF-TERNARY:
      DATABOOK-ID: 1
      TABLES:
        NRTL Non-randomness parameters-ternary:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides NRTL matrix parameters for a ternary mixture through binary pair rows.
          MATRIX-SYMBOL:
            - a constant: a
            - b constant: b
            - c constant: c
            - non-randomness parameter: alpha
          STRUCTURE:
            COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
            - [1,methanol|butyl-methyl-ether,methanol,CH3OH,l,0,0.1201,0,2.25,0,18.4,0,0.680715]
            - [2,methanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2152,0,-8.75,0,0.041,0,0.680715,0]
            - [1,ethanol|butyl-methyl-ether,ethanol,C2H5OH,l,0,0.1803,0,3.268,0,22.6,0,0.680715]
            - [2,ethanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2457,0,-12.48,0,0.052,0,0.680715,0]
"""

# ====================================================
# SECTION: MIXTURE COMPONENTS
# ====================================================
methanol = Component(
    name='methanol',
    formula='CH3OH',
    state='l'
)

ethanol = Component(
    name='ethanol',
    formula='C2H5OH',
    state='l'
)

butyl_methyl_ether = Component(
    name='butyl-methyl-ether',
    formula='C5H12O',
    state='l'
)

components = [methanol, ethanol, butyl_methyl_ether]
component_names = [component.name for component in components]

# ====================================================
# SECTION: BUILD MIXTURE MODEL SOURCE
# ====================================================
mixture_thermodb: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
    components=components,
    reference_content=REFERENCE_CONTENT,
    component_key='Name-State',
    mixture_key='Name',
)
print(f"mixture_thermodb: {type(mixture_thermodb)}")

if mixture_thermodb is None:
    raise ValueError("mixture_thermodb is None")

mixture_model_source: MixtureModelSource = build_mixture_model_source(
    mixture_thermodb=mixture_thermodb,
    mixture_key='Name',
)

model_source: ModelSource = build_model_source(
    source=[mixture_model_source],
)

# ====================================================
# SECTION: MAKE SOURCE
# ====================================================
source = Source(
    model_source=model_source,
    mixture_key='Name',
)
print(source)

print("Data symbols:")
print(source.data_symbols)

# NOTE: build_mixture_model_source sorts mixture ids alphabetically.
mixture_id = 'butyl-methyl-ether|ethanol|methanol'
matrix_prop = 'alpha'

# ====================================================
# SECTION: TABLE MATRIX DATA ACCESS
# ====================================================
matrix_data = source.get_matrix(
    mixture_name=mixture_id,
    prop_name=matrix_prop,
)

if not isinstance(matrix_data, TableMatrixData):
    raise TypeError(
        f"Expected TableMatrixData for {mixture_id}:{matrix_prop}, got {type(matrix_data)}"
    )

print("Matrix symbols:")
print(matrix_data.matrix_symbol)

print("Matrix data structure:")
print(matrix_data.matrix_data_structure())

print("Matrix table - selected:")
print(matrix_data.get_matrix_table(mode='selected'))

print("alpha methanol -> ethanol:")
print(source.matrix_ij(
    mixture_name=mixture_id,
    prop_name=matrix_prop,
    property='alpha | methanol | ethanol',
))

print("b methanol -> butyl-methyl-ether:")
print(source.matrix_property(
    mixture_name=mixture_id,
    prop_name='b',
    property='b_i_j',
    component_names=['methanol', 'butyl-methyl-ether'],
))

print("alpha ternary matrix:")
alpha_matrix = source.mat(
    mixture_name=mixture_id,
    prop_name=matrix_prop,
    property_name='alpha',
    component_names=component_names,
    symbol_format='numeric',
)
print(alpha_matrix)

if isinstance(alpha_matrix, np.ndarray):
    print(f"alpha ternary matrix shape: {alpha_matrix.shape}")

print("alpha ternary matrix as dict by formula-state:")
print(source.mat(
    mixture_name=mixture_id,
    prop_name=matrix_prop,
    property_name='alpha',
    component_names=component_names,
    symbol_format='alphabetic',
    component_key='Formula',
))

print("alpha ternary matrix using Component objects:")
print(source.matX(
    prop_name=matrix_prop,
    property_name='alpha',
    components=components,
    symbol_format='numeric',
))
