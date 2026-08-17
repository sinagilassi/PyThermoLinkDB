# import packages/modules
import os
from rich import print
from typing import Callable, Dict, Optional, Union, List, Any
import pyThermoDB as ptdb
# locals
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB.models import DataSource, EquationSource, ConstantsSource
# ! source
from pyThermoLinkDB.thermo import Source
# ! model source
from examples.model_source.model_source_2 import model_source, CO2

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
datasource: Dict[str, DataSource] = model_source.data_source
equationsource: Dict[str, EquationSource] = model_source.equation_source
constantssource: Dict[
    str,
    ConstantsSource
] | None = model_source.constants_source

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

# multiple specific data
# ! all loaded
comp_data_multiple_specific = source.get_props(
    'CO2-g',
    ['EnFo_IG', 'EnFus']
)
print("Component data for")
print(comp_data_multiple_specific)

# ! missing props
comp_data_multiple_specific = source.get_props(
    'CO2-g',
    ['EnFo_IG', 'EnFus', 'Unknown']
)
print("Component data for")
print(comp_data_multiple_specific)

# specific data symbols
comp_data_specific_symbol = source.get_prop_symbol('CO2-g', 'EnFo_IG')
print("Component data symbols for")
print(comp_data_specific_symbol)
