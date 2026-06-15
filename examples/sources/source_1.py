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

# symbols
data_symbols = source.data_symbols
equation_symbols = source.equation_symbols
constants_symbols = source.constants_symbols
print(data_symbols)
print(equation_symbols)
print(constants_symbols)

# ========================================
# SECTION: EQUATION SOURCE
# ========================================
# NOTE: make equation source core
eq_src = source.eq_builder(
    components=[CO2],
    prop_name='Cp_IG',
    # component_key='Name-Formula',
    component_keys=['Name-State', 'Formula-State', 'Name-Formula-State']
)
print(eq_src)
# >> check
if eq_src is None:
    raise

# NOTE: get equation symbols
eq_symbols = source.component_eq_symbols('CO2-g')
print("Equation symbols for")
print(eq_symbols)

# specific equation symbols
eq_symbols_specific = source.eq_symbol('CO2-g', 'Cp_IG')
print("Equation symbols for")
print(eq_symbols_specific)

# NOTE: evaluate equation source
eq_res = source.eq_eval(
    components=[CO2],
    eq_src_comp=eq_src,
    args_values={'T': 298.15}
)
print(eq_res)

# ========================================
# SECTION: DATA SOURCE
# ========================================
# NOTE: get component data
comp_data = source.get_dt('CO2-g')
print("Component data for")
print(comp_data)

# NOTE: get component data symbols
comp_data_symbols = source.get_dt_symbols('CO2-g')
print("Component data symbols for")
print(comp_data_symbols)

# specific data
comp_data_specific = source.get_prop('CO2-g', 'EnFo_IG')
print("Component data for")
print(comp_data_specific)

# specific data symbols
comp_data_specific_symbol = source.get_prop_symbol('CO2-g', 'EnFo_IG')
print("Component data symbols for")
print(comp_data_specific_symbol)

# ========================================
# SECTION: CONSTANTS SOURCE
# ========================================
# NOTE: access to constants source
# ! check availability of constant 'R'
check_0 = source.is_constant_available('R')
print(f"Is constant 'R' available? {check_0}")
# ! get constant 'R'
const_0 = source.const('R')
print(const_0)

# ! get constant 'R' symbols
const_0_symbol = source.const_symbol('R')
print(const_0_symbol)
