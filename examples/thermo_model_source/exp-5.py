"""Build a container holding model and custom thermodynamic sources."""

from examples.thermo_model_source.model_source_1 import model_source
from examples.thermo_model_source.custom_source_1 import custom_source
from examples.thermo_model_source.components_1 import components
from pythermodb_settings.models import CustomProperty
from pyThermoLinkDB.utils.thermo_source_tools import map_eq, map_prop
from pyThermoLinkDB.thermo import EquationSourceCore
from pyThermoLinkDB.models import (
    CustomSourceConfig,
    ModelSourceConfig,
)
from pyThermoLinkDB.builders import ThermoSourceHub, build_thermo_source
from rich import print
from pathlib import Path
import sys
from typing import Dict
import pycuc

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


thermo_source_hub: ThermoSourceHub | None = build_thermo_source(
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

print("\n[bold green]Validation quick checks[/bold green]")
print({
    "model_valid": thermo_source_hub.is_model_source_valid(),
    "model_all_requested": thermo_source_hub.has_all_model_requested(),
    "model_all_components": thermo_source_hub.has_all_model_components(),
    "custom_valid": thermo_source_hub.is_custom_source_valid(),
    "custom_all_requested": thermo_source_hub.has_all_custom_requested(),
    "custom_all_components": thermo_source_hub.has_all_custom_components(),
})

print("\n[bold green]Validation summary[/bold green]")
print(thermo_source_hub.validation_summary())

validation_reports = thermo_source_hub.validate_sources()

if validation_reports["model_source"] is not None:
    print("\n[bold green]Model validation details[/bold green]")
    print(validation_reports["model_source"].summary())
    print(validation_reports["model_source"].issues)

if validation_reports["custom_source"] is not None:
    print("\n[bold green]Custom validation details[/bold green]")
    print(validation_reports["custom_source"].summary())
    print(validation_reports["custom_source"].issues)

print("\n[bold cyan]Thermo source extraction[/bold cyan]")

# SECTION: Unit conversion function
# NOTE: create unit conversion function using pycuc
unit_conversion_fn = pycuc.convert_from_to

# NOTE: get MW source from custom source
mw_source = thermo_source_hub.get_comp_src(
    source_type="custom_source",
    symbol="MW",
)
# >> check
if mw_source is not None:
    # NOTE: map_prop returns a component-keyed dictionary and ordered values.
    mapped_mw = map_prop(
        data=mw_source,
        components=components,
        component_key="Formula-State",
        output_unit="kg/mol",
        unit_conversion_fn=unit_conversion_fn
    )
    if mapped_mw is not None:
        mw_comp, mw_values = mapped_mw
        print("[bold]Mapped MW component data[/bold]")
        print(mw_comp)
        print("[bold]Mapped MW values in component order[/bold]")
        print(mw_values)

# NOTE: get Cp_IG equation source from model source
model_cp_ig_eq: Dict[str, EquationSourceCore] | None = thermo_source_hub.get_comp_eq(
    source_type="model_source",
    symbol="Cp_IG",
)
# >> check
if model_cp_ig_eq is not None:
    cp_ig_eq_source: Dict[str, EquationSourceCore] = {
        "CO2-g": model_cp_ig_eq["CO2-g"],
        "ethylene-g": model_cp_ig_eq["C2H4-g"],
        "ethane": model_cp_ig_eq["C2H6-g"],
    }
    mapped_cp_ig_eq = map_eq(
        data=cp_ig_eq_source,
        components=components,
        component_key="Formula-State",
    )
    if mapped_cp_ig_eq is not None:
        cp_ig_eq_comp, cp_ig_eq_values = mapped_cp_ig_eq
        print("[bold]Mapped Cp_IG equation data[/bold]")
        print(cp_ig_eq_comp)
        print("[bold]Mapped Cp_IG equations in component order[/bold]")
        print(cp_ig_eq_values)
