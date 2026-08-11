# import libs
import os
from rich import print
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pythermodb_settings.models import CustomProperty, Component, CustomConstant
# ! from pyThermoLinkDB
from pyThermoLinkDB.builders import build_custom_model_source, ThermoCustomSource
# ! custom source
from examples.thermo_model_source.custom_source_1 import custom_source

# ====================================================
# SECTION: BUILD COMPONENT THERMODB
# ====================================================
# NOTE: parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(parent_dir)

# NOTE: thermodb directory
thermodb_dir = os.path.join(parent_dir, 'thermodb')
print(thermodb_dir)

# NOTE: create component
# ! propane
# carbon dioxide
CO2 = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g',
)

# Hydrogen
H2 = Component(
    name='hydrogen',
    formula='H2',
    state='g',
)

# methanol
CH3OH = Component(
    name='methanol',
    formula='CH3OH',
    state='g',
)

# ethanol
C2H5OH = Component(
    name='ethanol',
    formula='C2H5OH',
    state='g',
)

# water
H2O = Component(
    name='water',
    formula='H2O',
    state='g',
)

# Carbon monoxide
CO = Component(
    name='carbon monoxide',
    formula='CO',
    state='g',
)

# ethylene
C2H4 = Component(
    name='ethylene',
    formula='C2H4',
    state='g',
)

# ethane
C2H6 = Component(
    name='ethane',
    formula='C2H6',
    state='g',
)

# components
components = [C2H4, C2H6, CO2]

# # =======================================
# BUILD CUSTOM MODEL SOURCE
# =======================================
# NOTE: components configuration
components = [C2H4, C2H6, CO2]
component_key = 'Formula-State'

# NOTE: thermo data and constants to be extracted from the custom source
requested_data = ['MW', 'Cp_IG', 'Cp_LIQ', 'rho_LIQ']
requested_matrix_data = ['CUSTOM_MATRIX', 'CH4|C2H6']
requested_constants = [
    'dH_rxn',
    'Cp_LIQ_MIX_VOL',
    'R',
    'CUSTOM_CONST',
    'ANOTHER_CONST',
    'THIRD_CONST'
]

# NOTE: build custom model source
custom_model_src: ThermoCustomSource | None = build_custom_model_source(
    components=components,
    component_key=component_key,
    custom_source=custom_source,
    requested_data=requested_data,
    requested_matrix_data=requested_matrix_data,
    requested_constants=requested_constants,
    description="Example custom model source with custom constants",
    mode='log'  # options: 'silent', 'log', 'attach'
)

if custom_model_src is None:
    raise RuntimeError("Failed to build custom model source.")

print("\n[bold green]Custom matrix data[/bold green]")
for symbol in requested_matrix_data:
    entry = custom_model_src.thermo_src[symbol]
    matrix_src = entry["src"]

    print(f"\n[bold cyan]{symbol}[/bold cyan]")
    print("source =", matrix_src)
    print("value =", entry["value"])
    print("mode =", entry["mode"])

print("\n[bold green]Custom model source[/bold green]")
print(custom_model_src.thermo_src)
