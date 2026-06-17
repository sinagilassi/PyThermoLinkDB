# import libs
# import packages/modules
from rich import print
import pycuc
import pyThermoDB as ptdb
from pythermodb_settings.utils import set_component_id
# ! from pyThermoLinkDB
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import (
    mkeqss,
    EquationSourceCore,
    EquationSourcesCore,
)
from pyThermoLinkDB.utils.input_builder import validate_and_build_inputs
from pyThermoLinkDB.builders import build_thermo_model_source

# ! model source & components
from examples.model_source_1 import model_source, CO2, C2H5OH, CO, H2O


# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# BUILD MODEL SOURCE
# =======================================
# NOTE: components configuration
components = [CO2, C2H5OH, CO, H2O]
component_key = 'Name-State'

# NOTE: thermo data, equations, and constants to be extracted from the model source
thermo_data = ['EnFo_IG', 'Tc', 'Pc']
thermo_equations = ['Cp_IG', 'VaPr']
thermo_constants = ['R', 'dH_rxn']

# NOTE: build thermo model source
thermo_model_src = build_thermo_model_source(
    model_source=model_source,
    components=components,
    component_key=component_key,
    thermo_data=thermo_data,
    thermo_equations=thermo_equations,
    thermo_constants=thermo_constants
)

# print
print(thermo_model_src)
