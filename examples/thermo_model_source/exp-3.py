# import libs
import os
from rich import print
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pythermodb_settings.models import CustomProperty, Component
# ! from pyThermoLinkDB
from pyThermoLinkDB.models import CustomConstant
from pyThermoLinkDB.builders import build_custom_model_source, ThermoCustomSource

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

# ====================================================
# SECTION: thermo inputs
# ====================================================
# NOTE: molecular weight (MW) for the components in g/mol
molecular_weight = {
    "C2H4-g": CustomProperty(value=0.028, unit="kg/mol", symbol="MW"),
    "C2H6-g": CustomProperty(value=0.018, unit="kg/mol", symbol="MW"),
    "CO2-g": CustomProperty(value=0.046, unit="kg/mol", symbol="MW"),
}

# NOTE: optional constant gas heat capacities [J/mol.K]
constant_gas_heat_capacity = {
    "C2H4-g": CustomProperty(value=75.3, unit="J/mol.K", symbol="Cp_IG"),
    "C2H6-g": CustomProperty(value=75.3, unit="J/mol.K", symbol="Cp_IG"),
    "CO2-g": CustomProperty(value=75.3, unit="J/mol.K", symbol="Cp_IG"),
}

# NOTE: optional constant liquid heat capacities [J/mol.K]
constant_liquid_heat_capacity = {
    "C2H4-g": CustomProperty(value=81.1, unit="J/mol.K", symbol="Cp_LIQ"),
    "C2H6-g": CustomProperty(value=75.3, unit="J/mol.K", symbol="Cp_LIQ"),
    "CO2-g": CustomProperty(value=120.5, unit="J/mol.K", symbol="Cp_LIQ"),
}

# NOTE: constant liquid density (rho_LIQ) for the system in kg/m3
constant_liquid_density = {
    "C2H4-g": CustomProperty(value=570, unit="kg/m3", symbol="rho_LIQ"),
    "C2H6-g": CustomProperty(value=1000, unit="kg/m3", symbol="rho_LIQ"),
    "CO2-g": CustomProperty(value=789, unit="kg/m3", symbol="rho_LIQ"),
}

# NOTE: reaction enthalpy (dH_rxn) for the reactions in J/mol
reaction_enthalpies = {
    "r1": CustomProperty(value=-85000, unit="J/mol", symbol="dH_rxn"),
    "r2": CustomProperty(value=-80000, unit="J/mol", symbol="dH_rxn"),
}

# NOTE: volumetric heat capacity of liquid mixture in J/m3.K
liquid_mixture_volumetric_heat_capacity = CustomProperty(
    value=1100,
    unit="J/m3.K",
    symbol="Cp_LIQ_MIX_VOL"
)

# NOTE: universal gas constant (R) in J/mol.K
universal_gas_constant = CustomProperty(
    value=8.314, unit="J/mol.K", symbol="R"
)

# NOTE: custom source dictionary
custom_1 = CustomConstant(
    name="custom_constant",
    description="This is a custom constant for demonstration purposes.",
    value="GAS",
    unit=None,
    symbol="CUSTOM_CONST"
)

custom_2 = CustomConstant(
    name="another_custom_constant",
    description="This is another custom constant for demonstration purposes.",
    value=[1, 2, 3],
    unit="units",
    symbol="ANOTHER_CONST"
)

custom_3 = CustomConstant(
    name="third_custom_constant",
    description="This is a third custom constant for demonstration purposes.",
    value={"key1": "value1", "key2": "value2"},
    unit=None,
    symbol="THIRD_CONST"
)

# ! thermo inputs
custom_inputs = {
    "molecular_weight": molecular_weight,
    "constant_gas_heat_capacity": constant_gas_heat_capacity,
    "constant_liquid_heat_capacity": constant_liquid_heat_capacity,
    "constant_liquid_density": constant_liquid_density,
    "reaction_enthalpy": reaction_enthalpies,
    "liquid_mixture_volumetric_heat_capacity": liquid_mixture_volumetric_heat_capacity,
    "universal_gas_constant": universal_gas_constant,
    "custom_constant_1": custom_1,
    "custom_constant_2": custom_2,
    "custom_constant_3": custom_3,
}

# # =======================================
# BUILD CUSTOM MODEL SOURCE
# =======================================
# NOTE: components configuration
components = [C2H4, C2H6, CO2]
component_key = 'Formula-State'

# NOTE: thermo data and constants to be extracted from the custom source
requested_data = ['MW', 'Cp_IG', 'Cp_LIQ', 'rho_LIQ']
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
    custom_source=custom_inputs,
    requested_data=requested_data,
    requested_constants=requested_constants,
    description="Example custom model source with custom constants",
    mode='log'  # options: 'silent', 'log', 'attach'
)

if custom_model_src is None:
    raise RuntimeError("Failed to build custom model source.")

dynamic_attrs = custom_model_src.dynamic_attributes()

print("\n[bold green]Custom model source dynamic attributes[/bold green]")
print(dynamic_attrs)
