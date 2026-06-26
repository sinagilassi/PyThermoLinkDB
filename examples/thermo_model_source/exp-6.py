"""Build a container holding model and custom thermodynamic sources."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.thermo_model_source.model_source_1 import model_source
from examples.thermo_model_source.custom_source_1 import custom_source
from examples.thermo_model_source.components_1 import components
from pythermodb_settings.models import CustomProperty
from pyThermoLinkDB.utils.thermo_source_tools import map_eq, map_prop
from pyThermoLinkDB.thermo import EquationSourceCore
from pyThermoLinkDB.models import (
    CustomSourceConfig,
    ModelSourceConfig,
    SourceConfig,
    ThermoSourceHubConfig,
)
from pyThermoLinkDB.builders import (
    ThermoSourceHub,
    build_thermo_source_hub,
)
from rich import print
from typing import Dict
import pycuc


thermo_source_hub: ThermoSourceHub | None = build_thermo_source_hub(
    components=components,
    component_key="Formula-State",
    model_source=model_source,
    custom_source=custom_source,
    model_source_config=ModelSourceConfig(
        data=["EnFo_IG", "Tc", "Pc"],
        equations=["Cp_IG", "VaPr"],
        constants=["R", "dH_rxn"],
    ),
    custom_source_config=CustomSourceConfig(
        data=["MW", "Cp_IG", "Cp_LIQ", "rho_LIQ"],
        constants=[
            "dH_rxn",
            "Cp_LIQ_MIX_VOL",
            "R",
            "CUSTOM_CONST",
            "ANOTHER_CONST",
            "THIRD_CONST",
        ],
    ),
    description="Model and custom thermodynamic source container",
)

if thermo_source_hub is None:
    raise RuntimeError("Failed to build the thermodynamic source.")

# NOTE: thermo source hub
print("\n[bold cyan]Thermo source hub[/bold cyan]")
print(thermo_source_hub)

# NOTE: thermo source hub
print("\n[bold cyan]Thermo source hub[/bold cyan]")
print(thermo_source_hub.thermo_source_hub_types)

# NOTE: thermo source
print("\n[bold cyan]Thermo source[/bold cyan]")
print(thermo_source_hub.thermo_source)

# NOTE: symbols
print("\n[bold cyan]Thermo source symbols[/bold cyan]")
print(thermo_source_hub.model_source_symbols)
print(thermo_source_hub.custom_source_symbols)

# NOTE: Symbols & Modes
print("\n[bold cyan]Thermo source symbols and modes[/bold cyan]")
print(thermo_source_hub.model_source_symbol_modes)
print(thermo_source_hub.custom_source_symbol_modes)

# SECTION: thermo source hub configuration
thermo_source_hub_config: ThermoSourceHubConfig = {
    "Tc": SourceConfig(),
    "Pc": SourceConfig(),
    "EnFo_IG": SourceConfig(),
    "Cp_IG": SourceConfig(
        property_source="custom_source",
        equation_source="model_source",
    ),
    "R": SourceConfig(constants_source="model_source"),
}

print("\n[bold cyan]Thermo source registry[/bold cyan]")
print(thermo_source_hub.register_thermo_source(
    thermo_source_hub_config=thermo_source_hub_config,
))

print("\n[bold cyan]Thermo source registry with missing fields[/bold cyan]")
print(thermo_source_hub.register_thermo_source(
    thermo_source_hub_config=thermo_source_hub_config,
    include_missing=True,
))
