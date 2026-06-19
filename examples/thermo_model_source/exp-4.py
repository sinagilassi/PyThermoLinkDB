# import libs
import os
from rich import print
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pythermodb_settings.models import CustomProperty, Component, ComponentKey
# ! from pyThermoLinkDB
from pyThermoLinkDB.models import ModelSourceConfig, CustomSourceConfig
from pyThermoLinkDB.builders import build_thermo_source, ThermoSource
# ! components
from examples.thermo_model_source.components_1 import components
# ! model source
from examples.thermo_model_source.model_source_1 import model_source
# ! custom source
from examples.thermo_model_source.custom_source_1 import custom_source


# NOTE: parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(parent_dir)

# NOTE: thermodb directory
thermodb_dir = os.path.join(parent_dir, 'thermodb')
print(thermodb_dir)

# SECTION: build thermo source
# ! component key
component_key = "Name-State"

# NOTE: model source
model_source_config = ModelSourceConfig(
    data=['EnFo_IG', 'Tc', 'Pc'],
    equations=['Cp_IG', 'VaPr'],
    constants=['R', 'dH_rxn'],
)


# NOTE: custom source
custom_source_payload = CustomSourceConfig(
    data=['MW', 'Cp_IG', 'Cp_LIQ', 'rho_LIQ'],
    constants=[
        'dH_rxn',
        'Cp_LIQ_MIX_VOL',
        'R',
        'CUSTOM_CONST',
        'ANOTHER_CONST',
        'THIRD_CONST'
    ],
)
