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
from pyThermoLinkDB.thermo import mkdt, mkeq, mkeqs, EquationSourceCore, DataSourceCore
# ! model source
from examples.model_source_1 import model_source, CO2, C2H5OH

# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# ✅ MODEL SOURCE
# =======================================
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
# ✅ MAKE EQUATION/DATA SOURCE DIRECTLY
# =======================================
# NOTE: CO2 dt
CO2_dt = mkdt(
    component=CO2,
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
    component=CO2,
    model_source=model_source,
    component_key='Name-State',
)

# print
print(CO2_Cp_IG_eq)

# >> check
if CO2_Cp_IG_eq is not None and isinstance(CO2_Cp_IG_eq, EquationSourceCore):
    print(CO2_Cp_IG_eq.inputs)
    print(CO2_Cp_IG_eq.args)
    # fn
    if CO2_Cp_IG_eq.fn is not None:
        print(CO2_Cp_IG_eq.fn(T=298.15))
    print(CO2_Cp_IG_eq.calc(T=298.15, P=12))

# ! make equation source for a component including all equations
CO2_eqs = mkeqs(
    component=CO2,
    model_source=model_source,
    component_key='Name-State',
)
# print
print(CO2_eqs)

# ! make equation source
ethanol_eqs = mkeqs(
    component=C2H5OH,
    model_source=model_source,
    component_key='Name-State',
)
# print
print(ethanol_eqs)

# NOTE: >> check CO2 equations
if CO2_eqs is not None:
    print(CO2_eqs.equations())

    # >> make Cp_IG equation source
    Cp_IG_eq = CO2_eqs.eq(name='Cp_IG')
    print(Cp_IG_eq)
    if Cp_IG_eq is not None:
        # inputs
        print(Cp_IG_eq.inputs)
        # fn
        if Cp_IG_eq.fn is not None:
            print(Cp_IG_eq.fn(T=298.15))
        # calc
        print(Cp_IG_eq.calc(T=298.15, P=12))

    # >> make VaPr equation source
    VaPr_eq = CO2_eqs.eq(name='VaPr')
    print(VaPr_eq)
    if VaPr_eq is not None:
        # fn
        if VaPr_eq.fn is not None:
            print(VaPr_eq.fn(T=220))
        # calc
        print(VaPr_eq.calc(T=220))

# NOTE: >> check ethane equations
if ethanol_eqs is not None:
    print(ethanol_eqs.equations())

    # >> make Cp_IG equation source
    Cp_IG_eq = ethanol_eqs.eq(name='Cp_IG')
    print(Cp_IG_eq)
    if Cp_IG_eq is not None:
        # inputs
        print(Cp_IG_eq.inputs)
        # fn
        if Cp_IG_eq.fn is not None:
            print(Cp_IG_eq.fn(T=298.15))
        # calc
        print(Cp_IG_eq.calc(T=298.15, P=12))

    # >> make Cp_LIQ equation source
    Cp_LIQ_eq = ethanol_eqs.eq(name='Cp_LIQ')
    print(Cp_LIQ_eq)
    if Cp_LIQ_eq is not None:
        # inputs
        print(Cp_LIQ_eq.args)
        print(Cp_LIQ_eq.arg_symbols)
        print(Cp_LIQ_eq.inputs)
        print(Cp_LIQ_eq.arg_mappings)
        # fn
        if Cp_LIQ_eq.fn is not None:
            print(Cp_LIQ_eq.fn(T=298.15, Tc=302))
        # calc
        print(Cp_LIQ_eq.calc(T=298.15, Tc=302))
