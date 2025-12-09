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
    'carbon dioxide-g.pkl'
)

# NOTE: components
CO2_comp = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g'
)

# thermodb file
ethane_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'ethane-g.pkl'
)

ethane_comp = Component(
    name='ethane',
    formula='C2H6',
    state='g'
)

# =======================================
# SECTION: create thermodb source
# ======================================
# NOTE: component thermodb
CO2_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=CO2_comp,
    source=_thermodb_file
)

# NOTE: ethane thermodb
ethane_thermodb: ComponentThermoDBSource = ComponentThermoDBSource(
    component=ethane_comp,
    source=ethane_thermodb_file
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

# load and build model source
model_source: ModelSource = load_and_build_model_source(
    thermodb_sources=[CO2_thermodb, ethane_thermodb],
    rules=thermodb_rules,
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
dt1_ = datasource['CO2-g']['EnFo']
print(type(dt1_))
print(dt1_)

# equation
eq1_ = equationsource['CO2-g']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))


# =======================================
# ✅ MAKE EQUATION/DATA SOURCE DIRECTLY
# =======================================
# NOTE: CO2 dt
CO2_dt = mkdt(
    component=CO2_comp,
    model_source=model_source,
    component_key='Name-State',
)
# print
print(CO2_dt)

# >> check
if CO2_dt is not None:
    print(CO2_dt.props())
    print(CO2_dt.prop(name='EnFo'))


# NOTE : CO2 equation
# ! make equation source for a component and a specific equation
CO2_Cp_IG_eq = mkeq(
    name='Cp_IG',
    component=CO2_comp,
    model_source=model_source,
    component_key='Name-State',
)

# print
print(CO2_Cp_IG_eq)

# >> check
if CO2_Cp_IG_eq is not None:
    print(CO2_Cp_IG_eq.inputs)
    print(CO2_Cp_IG_eq.args)
    print(CO2_Cp_IG_eq.fn(T=298.15))
    print(CO2_Cp_IG_eq.calc(T=298.15, P=12))

# ! make equation source for a component including all equations
CO2_eqs = mkeqs(
    component=CO2_comp,
    model_source=model_source,
    component_key='Name-State',
)
# print
print(CO2_eqs)

# ! make equation source
ethane_eqs = mkeqs(
    component=ethane_comp,
    model_source=model_source,
    component_key='Name-State',
)
# print
print(ethane_eqs)

# NOTE: >> check CO2 equations
# if CO2_eqs is not None:
#     print(CO2_eqs.equations())

#     # >> make Cp_IG equation source
#     Cp_IG_eq = CO2_eqs.eq(name='Cp_IG')
#     print(Cp_IG_eq)
#     if Cp_IG_eq is not None:
#         # inputs
#         print(Cp_IG_eq.inputs)
#         # fn
#         print(Cp_IG_eq.fn(T=298.15))
#         # calc
#         print(Cp_IG_eq.calc(T=298.15, P=12))

#     # >> make VaPr equation source
#     VaPr_eq = CO2_eqs.eq(name='VaPr')
#     print(VaPr_eq)
#     if VaPr_eq is not None:
#         print(VaPr_eq.fn(T=220))
#         # calc
#         print(VaPr_eq.calc(T=220))

# NOTE: >> check ethane equations
if ethane_eqs is not None:
    print(ethane_eqs.equations())

    # # >> make Cp_IG equation source
    # Cp_IG_eq = ethane_eqs.eq(name='Cp_IG')
    # print(Cp_IG_eq)
    # if Cp_IG_eq is not None:
    #     # inputs
    #     print(Cp_IG_eq.inputs)
    #     # fn
    #     print(Cp_IG_eq.fn(T=298.15))
    #     # calc
    #     print(Cp_IG_eq.calc(T=298.15, P=12))

    # >> make Cp_LIQ equation source
    Cp_LIQ_eq = ethane_eqs.eq(name='Cp_LIQ')
    print(Cp_LIQ_eq)
    if Cp_LIQ_eq is not None:
        # inputs
        print(Cp_LIQ_eq.args)
        print(Cp_LIQ_eq.inputs)
        print(Cp_LIQ_eq.arg_mappings)
        print(Cp_LIQ_eq.fn(T=298.15))
        # calc
        print(Cp_LIQ_eq.calc(T=298.15))
