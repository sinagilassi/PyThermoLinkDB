# import libs
import logging
import os
from typing import Dict
import warnings
from rich import print
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pythermodb_settings.models import CustomProperty, Component

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

# ! thermo inputs
custom_inputs = {
    "molecular_weight": molecular_weight,
    "constant_gas_heat_capacity": constant_gas_heat_capacity,
    "constant_liquid_heat_capacity": constant_liquid_heat_capacity,
    "constant_liquid_density": constant_liquid_density,
    "reaction_enthalpy": reaction_enthalpies,
    "liquid_mixture_volumetric_heat_capacity": liquid_mixture_volumetric_heat_capacity,
}
