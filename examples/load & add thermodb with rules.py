# import packages/modules
from typing import Dict, Optional
import os
from rich import print
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import load_and_build_model_source
from pyThermoLinkDB.models import ModelSource
import pyThermoDB as ptdb
from pythermodb_settings.models import (
    Component,
    ComponentRule,
    ComponentThermoDBSource,
    MixtureThermoDBSource
)
from pyThermoDB.core import TableMatrixData

# check version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================
# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current dir: {current_dir}")

# NOTE: thermodb configurations
# methane gas thermodb file
_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'methane-g.pkl'
)

# binary mixture thermodb file
_mixture_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'mixture methanol-ethanol.pkl'
)

# NOTE: components
methane = Component(
    name='Methane',
    formula='CH4',
    state='g'
)

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

# =======================================
# SECTION: create thermodb source
# ======================================
# NOTE: component thermodb
methane_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=methane,
    source=_thermodb_file
)

# NOTE: mixture thermodb
mixture_components: MixtureThermoDBSource = MixtureThermoDBSource(
    components=[methanol, ethanol],
    source=_mixture_thermodb_file
)

# =======================================
# 🏗️ LOAD & BUILD
# =======================================
# update thermodb rule
thermodb_rules: Dict[str, Dict[str, ComponentRule]] = {
    'ALL': {
        'DATA': {
            'critical-pressure': 'Pc',
            'critical-temperature': 'Tc',
            'acentric-factor': 'AcFa'
        },
        'EQUATIONS': {
            'CUSTOM-REF-1::vapor-pressure': 'VaPr',
            'CUSTOM-REF-1::ideal-gas-heat-capacity': 'Cp_IG'
        }
    },
    'CH4-g': {
        'DATA': {
            'critical-pressure': 'Pc',
            'critical-temperature': 'Tc',
            'acentric-factor': 'AcFa'
        },
        'EQUATIONS': {
            'CUSTOM-REF-1::vapor-pressure': 'VaPr',
            'CUSTOM-REF-1::ideal-gas-heat-capacity': 'Cp_IG'
        }
    },
    'Methane-g': {
        'DATA': {
            'critical-pressure': 'Pc',
            'critical-temperature': 'Tc',
            'acentric-factor': 'AcFa'
        },
        'EQUATIONS': {
            'CUSTOM-REF-1::vapor-pressure': 'VaPr',
            'CUSTOM-REF-1::ideal-gas-heat-capacity': 'Cp_IG'
        }
    }
}

model_source2: ModelSource = load_and_build_model_source(
    thermodb_sources=[methane_thermodb, mixture_components],
    rules=thermodb_rules,
)
print(model_source2)

# get data source and equation source
datasource = model_source2.data_source
equationsource = model_source2.equation_source

# =======================================
# ✅ TEST
# =======================================
# NOTE: by formula-state
# data
dt1_ = datasource['CH4-g']['EnFo']
print(type(dt1_))
print(dt1_)

# equation
eq1_ = equationsource['CH4-g']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))

eq1_ = equationsource['Methane-CH4']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))

# NOTE: by name-state
# data
dt2_ = datasource['Methane-g']['EnFo']
print(type(dt2_))
print(dt2_)
# equation
eq2_ = equationsource['Methane-g']['Cp_IG']
print(type(eq2_))
print(eq2_)
print(eq2_.args)

# NOTE: by mixture name (should be in order alphabetically)
# data
dt3_ = datasource['ethanol|methanol']['a']
# >> check data table matrix
if not isinstance(dt3_, TableMatrixData):
    raise ValueError("dt3_ is not TableMatrixData")
print(dt3_)
print(type(dt3_))
print(dt3_.matrix_table)
print(dt3_.matrix_symbol)
print(dt3_.matrix_data_structure())

# NOTE: old format
print(dt3_.get_matrix_property(
    "alpha_i_j",
    [ethanol.name, methanol.name],
    symbol_format='alphabetic'
)
)

nrtl_data_ = f"a_{ethanol.name}_{methanol.name}"
alpha_ij = dt3_.ijs(nrtl_data_)
print(alpha_ij)
nrtl_data_ = f"a | {ethanol.name} | {methanol.name}"
alpha_ij = dt3_.ijs(nrtl_data_)
print(alpha_ij)
