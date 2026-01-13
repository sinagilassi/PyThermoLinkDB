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
# carbon dioxide gas thermodb file
CO2_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'carbon dioxide-g-nasa.pkl'
)

# NOTE: components
# ! CO2
CO2 = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g'
)

# =======================================
# SECTION: create thermodb source
# ======================================
# NOTE: component thermodb
CO2_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=CO2,
    source=CO2_thermodb_file
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

# ! with rules
# model_source2: ModelSource = load_and_build_model_source(
#     thermodb_sources=[
#         CO2_thermodb
#     ],
#     rules=thermodb_rules,
# )
# print(model_source2)

# ! without rules
model_source1: ModelSource = load_and_build_model_source(
    thermodb_sources=[
        CO2_thermodb
    ],
    original_equation_label=False
)
print(model_source1)

# get data source and equation source
datasource = model_source1.data_source
equationsource = model_source1.equation_source

# =======================================
# ✅ TEST
# =======================================
# NOTE: by formula-state
# equation
# ! nasamin for CO2-g
eq1_ = equationsource['CO2-g']['nasamin']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.parms)
print(eq1_.parms_values)

# ! nasamax for CO2-g
eq2_ = equationsource['CO2-g']['nasamax']
print(type(eq2_))
print(eq2_)
print(eq2_.args)
print(eq2_.parms)
print(eq2_.parms_values)
