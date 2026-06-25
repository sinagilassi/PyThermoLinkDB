# import libs
from pythermodb_settings.models import CustomProperty, CustomConstant
# ! from pyThermoLinkDB


# ====================================================
# SECTION: custom thermo
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
custom_source = {
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
