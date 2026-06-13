# import packages/modules
import os
from rich import print
from typing import Callable, Dict, Optional, Union, List, Any
import pyThermoDB as ptdb
# locals
import pyThermoLinkDB as ptdblink
# ! source
from pyThermoLinkDB.thermo import Source
# ! model source
from examples.model_source_2 import model_source, CO2

# ! version
print(ptdb.__version__)
print(ptdblink.__version__)

# ====================================================
# SECTION: BUILD COMPONENT THERMODB
# ====================================================
# NOTE: parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(parent_dir)

# NOTE: thermodb directory
thermodb_dir = os.path.join(parent_dir, 'thermodb')
print(thermodb_dir)

# ====================================================
# SECTION: THERMODB LINK CONFIGURATION
# ====================================================

# build datasource & equationsource
datasource = model_source.data_source
equationsource = model_source.equation_source
constantssource = model_source.constants_source
# symbols
data_symbols = model_source.data_symbols
equation_symbols = model_source.equation_symbols
constants_symbols = model_source.constants_symbols

# =======================================
# SECTION: ✅ MAKE SOURCE
# =======================================
# component key
component_key = 'Formula-State'
# init source
source = Source(
    model_source=model_source,
    component_key=component_key
)
print(source)

# NOTE: make equation source core
eq_src = source.eq_builder(
    components=[CO2],
    prop_name='Cp_IG',
    # component_key='Name-Formula',
    component_keys=['Name-State', 'Formula-State', 'Name-Formula-State']
)
print(eq_src)

# NOTE: get component data
comp_data = source.get_dt('CO2-g')
print("Component data for")
print(comp_data)

# specific data
comp_data_specific = source.get_prop('CO2-g', 'EnFo_IG')
print("Component data for")
print(comp_data_specific)

# NOTE: access to constants source
# ! check availability of constant 'R'
check_0 = source.is_constant_available('R')
print(f"Is constant 'R' available? {check_0}")
# ! get constant 'R'
const_0 = source.const('R')
print(const_0)
