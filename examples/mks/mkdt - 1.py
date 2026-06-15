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
if CO2_dt is None:
    raise ValueError("Failed to create data source for CO2.")

# results
# ! all properties
print(CO2_dt.props)
print(CO2_dt.all_props())

# ! available properties
print(CO2_dt.is_prop_available('EnFo_IG'))
print(CO2_dt.is_prop_available('Unknown_Prop'))

# ! check a list of properties
print(CO2_dt.check_props_availability(['EnFo_IG', 'Cp_IG']))

# ! specific property
print(CO2_dt.prop(name='EnFo_IG'))
print(CO2_dt.select(symbol='EnFo_IG'))
