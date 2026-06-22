"""Build a container holding model and custom thermodynamic sources."""

from pathlib import Path
import sys

from rich import print

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pyThermoLinkDB.builders import ThermoSource, build_thermo_source
from pyThermoLinkDB.models import CustomSourceConfig, ModelSourceConfig

from examples.thermo_model_source.components_1 import components
from examples.thermo_model_source.custom_source_1 import custom_source
from examples.thermo_model_source.model_source_1 import model_source


thermo_source: ThermoSource | None = build_thermo_source(
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

if thermo_source is None:
    raise RuntimeError("Failed to build the thermodynamic source.")

if thermo_source.thermo_model_source is not None:
    print("\n[bold cyan]Model thermo source[/bold cyan]")
    print(thermo_source.thermo_model_source.thermo_src)

if thermo_source.thermo_custom_source is not None:
    print("\n[bold cyan]Custom thermo source[/bold cyan]")
    print(thermo_source.thermo_custom_source.thermo_src)
