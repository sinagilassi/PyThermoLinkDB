# import packages/modules
from typing import Dict
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
)
from pyThermoLinkDB.thermo import mkdt, mkeq, mkeqs
from pyThermoLinkDB.thermo import Source
from pyThermoLinkDB.thermo.equation_sources import EquationSourceCore

# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================
# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current dir: {current_dir}")

# NOTE: thermodb configurations
# thermodb file
_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'carbon dioxide.pkl'
)

# NOTE: components
CO2_comp = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g'
)

# thermodb file
ethanol_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'ethanol.pkl'
)

ethanol_comp = Component(
    name='ethanol',
    formula='C2H5OH',
    state='l'
)

# =======================================
# SECTION: create thermodb source
# ======================================
# NOTE: component thermodb
CO2_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=CO2_comp,
    source=_thermodb_file
)

# ! ethanol
ethanol_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=ethanol_comp,
    source=ethanol_thermodb_file
)

# =======================================
# 🏗️ LOAD & BUILD
# =======================================
# update thermodb rule
thermodb_rules: Dict[str, Dict[str, ComponentRule]] = {
    'carbon dioxide-g': {
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
}

# NOTE: load and build model source
# ! with rules
# model_source: ModelSource = load_and_build_model_source(
#     thermodb_sources=[
#         CO2_thermodb,
#         ethanol_thermodb
#     ],
#     rules=thermodb_rules,
#     original_equation_label=False
# )
# print(model_source)

# ! without rules & original labels is True
model_source: ModelSource = load_and_build_model_source(
    thermodb_sources=[
        CO2_thermodb,
        ethanol_thermodb
    ],
    original_equation_label=True
)
print(model_source)

# ! without rules & original labels is False
model_source: ModelSource = load_and_build_model_source(
    thermodb_sources=[
        CO2_thermodb,
        ethanol_thermodb
    ],
    original_equation_label=False
)
print(model_source)

# get data source and equation source
datasource = model_source.data_source
equationsource = model_source.equation_source

# =======================================
# ✅ TEST
# =======================================
# NOTE: by formula-state
# data
dt1_ = datasource['CO2-g']['EnFo_IG']
print(type(dt1_))
print(dt1_)

# equation
eq1_ = equationsource['CO2-g']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))


# =======================================
# ✅ MAKE SOURCE
# =======================================
# component key
component_key = 'Formula-State'
# init source
source = Source(
    model_source=model_source,
    component_key=component_key
)
print(source)

# make equation source core
eq_src = source.eq_builder(
    components=[CO2_comp],
    prop_name='Cp_IG',
    # component_keys=['Name-State', 'Formula-State', 'Name-Formula']
)
print(eq_src)
