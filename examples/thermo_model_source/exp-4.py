"""Build a container holding model and custom thermodynamic sources."""

from rich import print
from pyThermoLinkDB.builders import ThermoSourceHub, build_thermo_source
from pyThermoLinkDB.models import (
    CustomSourceConfig,
    ModelSourceConfig,
)
from pyThermoLinkDB.thermo import EquationSourceCore
from pythermodb_settings.models import CustomProperty, CustomConstant
from examples.thermo_model_source.components_1 import components
from examples.thermo_model_source.custom_source_1 import custom_source
from examples.thermo_model_source.model_source_1 import model_source
from pathlib import Path
import sys
from typing import Dict, Any, List

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

# NOTE: get the full source entry for a model data symbol
model_tc: Dict[str, Any] | None = thermo_source_hub.get(
    source_name="model_source",
    symbol="Tc",
)
print("[bold]Model Tc entry[/bold]")
print(model_tc)

# ! get source
model_tc_src: Dict[str, CustomProperty] | None = thermo_source_hub.get_comp_src(
    source_type="model_source",
    symbol="Tc",
)
print("[bold]Model Tc component sources[/bold]")
print(model_tc_src)

# NOTE: get source modes for symbols
model_tc_mode: List[str] | None = thermo_source_hub.get_mode(
    source_type="model_source",
    symbol="Tc",
)
custom_cp_ig_mode: List[str] | None = thermo_source_hub.get_mode(
    source_type="custom_source",
    symbol="Cp_IG",
)
custom_cp_ig_has_data: bool = thermo_source_hub.has_mode(
    source_type="custom_source",
    symbol="Cp_IG",
    mode="data",
)
custom_cp_ig_has_equation: bool = thermo_source_hub.has_mode(
    source_type="custom_source",
    symbol="Cp_IG",
    mode="equation",
)
print("[bold]Model Tc mode[/bold]")
print(model_tc_mode)
print("[bold]Custom Cp_IG mode[/bold]")
print(custom_cp_ig_mode)
print("[bold]Custom Cp_IG mode checks[/bold]")
print({
    "has_data": custom_cp_ig_has_data,
    "has_equation": custom_cp_ig_has_equation,
})

# NOTE: get a specific field from the model source entry
model_tc_values: Any = thermo_source_hub.get_item(
    source_type="model_source",
    symbol="Tc",
    item="value",
)
print("[bold]Model Tc values[/bold]")
print(model_tc_values)

# NOTE: get component-wise data from the custom source
custom_mw: Dict[str, float] | None = thermo_source_hub.get_comp_dt(
    source_type="custom_source",
    symbol="MW",
)
print("[bold]Custom MW component data[/bold]")
print(custom_mw)

# NOTE: get component-wise source objects from the custom source
custom_mw_src: Dict[str, CustomProperty] | None = thermo_source_hub.get_comp_src(
    source_type="custom_source",
    symbol="MW",
)
print("[bold]Custom MW component sources[/bold]")
print(custom_mw_src)

# NOTE: get component-wise values from the custom source
custom_cp_ig_values: List[float] | None = thermo_source_hub.get_comp_values(
    source_type="custom_source",
    symbol="Cp_IG",
)
print("[bold]Custom Cp_IG component values[/bold]")
print(custom_cp_ig_values)


# NOTE: get component-wise equations from the model source
model_cp_ig_eq: Dict[str, EquationSourceCore] | None = thermo_source_hub.get_comp_eq(
    source_type="model_source",
    symbol="Cp_IG",
)
print("[bold]Model Cp_IG component equations[/bold]")
print(model_cp_ig_eq)

# ! mode
model_cp_ig_eq_mode: List[str] | None = thermo_source_hub.get_mode(
    source_type="model_source",
    symbol="Cp_IG",
)
print("[bold]Model Cp_IG component equation modes[/bold]")
print(model_cp_ig_eq_mode)

# NOTE: get constant values from model and custom sources
model_r: Any = thermo_source_hub.get_const(
    source_type="model_source",
    symbol="R",
)
custom_constant: Any = thermo_source_hub.get_const(
    source_type="custom_source",
    symbol="CUSTOM_CONST",
)
model_r_src: CustomConstant | None = thermo_source_hub.get_const_src(
    source_type="model_source",
    symbol="R",
)
custom_constant_src: CustomConstant | None = thermo_source_hub.get_const_src(
    source_type="custom_source",
    symbol="CUSTOM_CONST",
)
print("[bold]Model R constant[/bold]")
print(model_r)
print("[bold]Model R constant source[/bold]")
print(model_r_src)
print("[bold]Custom constant[/bold]")
print(custom_constant)
print("[bold]Custom constant source[/bold]")
print(custom_constant_src)

# NOTE: reorder component-wise output with a different requested component order
reordered_components = list(reversed(components))
custom_mw_reordered: Dict[str, Any] | None = thermo_source_hub.get(
    source_name="custom_source",
    symbol="MW",
    components=reordered_components,
)
print("[bold]Custom MW entry in reversed component order[/bold]")
print(custom_mw_reordered)
