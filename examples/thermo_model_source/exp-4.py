"""Build and inspect a combined thermodynamic source without mutating it."""

from rich import print

from pyThermoLinkDB.builders import ThermoSource, build_thermo_source
from pyThermoLinkDB.models import CustomSourceConfig, ModelSourceConfig

from examples.thermo_model_source.components_1 import components
from examples.thermo_model_source.custom_source_1 import custom_source
from examples.thermo_model_source.model_source_1 import model_source


# ====================================================
# SECTION: Source Configuration
# ====================================================
# NOTE: The custom example uses Formula-State component IDs such as "CO2-g".
component_key = "Formula-State"

model_source_config = ModelSourceConfig(
    data=["EnFo_IG", "Tc", "Pc"],
    equations=["Cp_IG", "VaPr"],
    constants=["R", "dH_rxn"],
)

custom_source_config = CustomSourceConfig(
    data=["MW", "Cp_IG", "Cp_LIQ", "rho_LIQ"],
    constants=[
        "dH_rxn",
        "Cp_LIQ_MIX_VOL",
        "R",
        "CUSTOM_CONST",
        "ANOTHER_CONST",
        "THIRD_CONST",
    ],
)


# ====================================================
# SECTION: Build Thermo Source
# ====================================================
thermo_source: ThermoSource | None = build_thermo_source(
    components=components,
    component_key=component_key,
    model_source=model_source,
    custom_source=custom_source,
    model_source_config=model_source_config,
    custom_source_config=custom_source_config,
    description="Model and custom thermodynamic source example",
)

if thermo_source is None:
    raise RuntimeError("Failed to build the thermodynamic source.")


# ====================================================
# SECTION: Registry Inspection
# ====================================================
# Both sources remain under separate registry keys.
print("\n[bold cyan]Source keys[/bold cyan]")
print(list(thermo_source.source))

print("\n[bold cyan]Available symbols by source and category[/bold cyan]")
print(thermo_source.available())

print("\n[bold cyan]Selected symbol lists[/bold cyan]")
print("Model data:", thermo_source.list_symbols("data", "model"))
print("Model equations:", thermo_source.list_symbols("equations", "model"))
print("Custom data:", thermo_source.list_symbols("data", "custom"))
print("Custom constants:", thermo_source.list_symbols("constants", "custom"))

print("\n[bold cyan]Availability checks[/bold cyan]")
print("Model has Tc:", thermo_source.has("Tc", "data", "model"))
print("Custom has MW:", thermo_source.has("MW", "data", "custom"))
print("Custom has VaPr equation:", thermo_source.has("VaPr", "equations", "custom"))


# ====================================================
# SECTION: Value Lookup
# ====================================================
# Explicit source selection performs a direct lookup with no precedence rule.
print("\n[bold cyan]Explicit source values[/bold cyan]")
print("Model Tc values:", thermo_source.get("Tc", "data", "model"))
print("Custom MW values:", thermo_source.get("MW", "data", "custom"))
print("Custom R value:", thermo_source.get("R", "constants", "custom"))

# Equation values are not evaluated during source construction. Request the
# source accessor instead of the default "value" attribute.
print("Model Cp_IG equation sources:")
print(thermo_source.get("Cp_IG", "equations", "model", attribute="src"))


# ====================================================
# SECTION: Precedence Selection and Conflicts
# ====================================================
# ``resolve`` selects one source; it does not merge their source dictionaries.
print("\n[bold cyan]Precedence selection[/bold cyan]")
print("R (custom first):", thermo_source.resolve("R", "constants"))
print(
    "R (model first):",
    thermo_source.resolve(
        "R",
        "constants",
        precedence=("model", "custom"),
    ),
)

print("\n[bold cyan]Symbols present in both sources[/bold cyan]")
print(thermo_source.find_conflicts())


# ====================================================
# SECTION: Component Utilities
# ====================================================
component_id = "CO2-g"

print("\n[bold cyan]Component-level access[/bold cyan]")
print(
    f"MW for {component_id}:",
    thermo_source.get_component("MW", component_id, "custom"),
)
print(
    "Components with custom MW:",
    thermo_source.components_for("MW", "custom"),
)
print(
    "Custom MW is complete:",
    thermo_source.is_complete("MW", "custom"),
)


# ====================================================
# SECTION: Validation and Reporting
# ====================================================
required_symbols = {
    "data": ["Tc", "Pc", "MW", "rho_LIQ"],
    "equations": ["Cp_IG", "VaPr"],
    "constants": ["R", "dH_rxn"],
}

print("\n[bold cyan]Missing required symbols[/bold cyan]")
print(thermo_source.missing(required_symbols))

validation = thermo_source.validate(required=required_symbols)
print("\n[bold cyan]Validation result[/bold cyan]")
print(validation)

print("\n[bold cyan]Source summary[/bold cyan]")
print(thermo_source.summary())


# ====================================================
# SECTION: Separate Serialization
# ====================================================
serialized_source = thermo_source.to_dict()

print("\n[bold cyan]Serialized source namespaces[/bold cyan]")
print(list(serialized_source))
print("Model categories:", list(serialized_source["model_source"]))
print("Custom categories:", list(serialized_source["custom_source"]))
