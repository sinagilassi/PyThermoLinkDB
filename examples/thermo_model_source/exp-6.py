"""Build a container holding model and custom thermodynamic sources."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.thermo_model_source.model_source_2 import model_source
from examples.thermo_model_source.custom_source_1 import custom_source
from examples.thermo_model_source.components_1 import (
    C2H4,
    C2H6,
    CO2,
    C2H5OH,
    CH3OH,
)
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


components = [C2H4, C2H6, CO2]
mixture_1 = [CH3OH, C2H5OH]
mixtures = [mixture_1]


thermo_source_hub: ThermoSourceHub | None = build_thermo_source_hub(
    components=components,
    component_key="Formula-State",
    mixtures=mixtures,
    mixture_key="Name",
    model_source=model_source,
    custom_source=custom_source,
    model_source_config=ModelSourceConfig(
        data=["EnFo_IG", "Tc", "Pc"],
        equations=["Cp_IG", "VaPr"],
        matrix_data=["a", "b", "c", "alpha"],
        constants=["R", "dH_rxn"],
    ),
    custom_source_config=CustomSourceConfig(
        data=["MW", "Cp_IG", "Cp_LIQ", "rho_LIQ"],
        matrix_data=["CUSTOM_MATRIX", "CH4|C2H6"],
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
    "alpha": SourceConfig(
        property_source=None,
        equation_source=None,
        constants_source=None,
        matrix_data_source="model_source",
    ),
    "CUSTOM_MATRIX": SourceConfig(
        property_source=None,
        equation_source=None,
        constants_source=None,
        matrix_data_source="custom_source",
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
