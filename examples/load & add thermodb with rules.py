# import packages/modules
from typing import Dict, Optional
import os
from rich import print
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB.models import ModelSource
import pyThermoDB as ptdb
from pythermodb_settings.models import Component, ComponentRule, ComponentThermoDBSource

# check version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================
# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current dir: {current_dir}")

# NOTE: CO2
_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'methane-g.pkl'
)

# NOTE: components
_component = Component(
    name='Methane',
    formula='CH4',
    state='g'
)

# NOTE: component thermodb
_component_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=_component,
    source=_thermodb_file
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

model_source2: ModelSource = ptdblink.load_and_build_model_source(
    thermodb_sources=[_component_thermodb],
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
