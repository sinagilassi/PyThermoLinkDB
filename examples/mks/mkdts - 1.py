# import packages/modules
from rich import print
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import mkdts, DataSourceCore
from pythermodb_settings.utils import set_component_id

# ! model source & components
from examples.model_source_1 import model_source, CO2, C2H5OH


# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# MODEL SOURCE
# =======================================
datasource = model_source.data_source
equationsource = model_source.equation_source

# =======================================
# TEST
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
# MAKE DATA SOURCES DIRECTLY
# =======================================
components = [CO2, C2H5OH]
component_key = 'Name-State'

# NOTE: build data sources for all components
data_sources: dict[str, DataSourceCore] | None = mkdts(
    components=components,
    model_source=model_source,
    component_key=component_key,
)

# print
print(data_sources)

# >> check
if data_sources is None:
    raise ValueError("Failed to create data sources.")

# =======================================
# DICTIONARY KEYS
# =======================================
component_ids = [
    set_component_id(component, component_key)
    for component in components
]
print(component_ids)
print(data_sources.keys())

# =======================================
# ACCESS CO2 DATA SOURCE
# =======================================
CO2_id = set_component_id(CO2, component_key)
CO2_dt = data_sources[CO2_id]

# ! all properties
print(CO2_dt.props)
print(CO2_dt.all_props())

# ! all property symbols
print(CO2_dt.props_symbols)

# ! available properties
print(CO2_dt.is_prop_available('EnFo_IG'))
print(CO2_dt.is_prop_available('Unknown_Prop'))

# ! check a list of properties
print(CO2_dt.check_availability(['EnFo_IG', 'Cp_IG']))

# ! all properties available
print(CO2_dt.all_available(['EnFo_IG', 'Tc', 'Vc']))
print(CO2_dt.all_available(['EnFo_IG', 'Cp_IG']))

# ! specific property
print(CO2_dt.prop(name='EnFo_IG'))
print(CO2_dt.select(symbol='EnFo_IG'))

# =======================================
# ACCESS ETHANOL DATA SOURCE
# =======================================
ethanol_id = set_component_id(C2H5OH, component_key)
ethanol_dt = data_sources[ethanol_id]

print(ethanol_dt.props)
print(ethanol_dt.props_symbols)
print(ethanol_dt.is_prop_available('EnFo_IG'))
