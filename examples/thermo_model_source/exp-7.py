"""Register thermo source selections from string content."""

from pathlib import Path
import sys
from typing import Any

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
)
from pyThermoLinkDB.builders import (
    ThermoSourceHub,
    build_thermo_source_hub,
)
from pyThermoLinkDB.utils import thermo_source_hub_config_from_str
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
print("\n[bold cyan]Thermo source hub type[/bold cyan]")
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
thermo_source_hub_config = """
Tc: model_source
Pc: model_source
EnFo_IG: model_source
Cp_IG:
  property_source: custom_source
  equation_source: model_source
alpha:
  matrix_data_source: model_source
CUSTOM_MATRIX:
  matrix_data_source: custom_source
R:
  constants_source: model_source
"""

print("\n[bold cyan]Thermo source registry[/bold cyan]")
thermo_source_registry = thermo_source_hub.register_thermo_source(
    thermo_source_hub_config=thermo_source_hub_config,
    components=components,
    mixtures=mixtures,
)
print(thermo_source_registry)

print("\n[bold cyan]Thermo source registry with missing fields[/bold cyan]")
print(thermo_source_hub.register_thermo_source(
    thermo_source_hub_config=thermo_source_hub_config,
    components=components,
    mixtures=mixtures,
    include_missing=True,
))


# SECTION: access after registry
print("\n[bold cyan]Access after registry[/bold cyan]")

# NOTE:
# register_thermo_source() accepts the YAML string content above and converts
# it to ThermoSourceHubConfig before resolving sources. For property/constant/
# matrix selections, the selected source is stored in "src". For equation
# selections, the selected equation source is stored in "eq".

# NOTE: Tc uses string shorthand, so every source field is set to "model_source".
tc_src = thermo_source_registry["Tc"]["src"]
tc_values = {
    component_id: prop.value
    for component_id, prop in tc_src.items()
}
print("[bold]Tc source objects selected by registry[/bold]")
print(tc_src)
print("[bold]Tc values from registry source objects[/bold]")
print(tc_values)

# NOTE: Cp_IG is configured to use custom_source for property data and
# model_source for equation data.
cp_ig_src = thermo_source_registry["Cp_IG"]["src"]
cp_ig_eq = thermo_source_registry["Cp_IG"]["eq"]
cp_ig_values = {
    component_id: prop.value
    for component_id, prop in cp_ig_src.items()
}
print("[bold]Cp_IG property values from custom source[/bold]")
print(cp_ig_values)
print("[bold]Cp_IG equation sources from model source[/bold]")
print(cp_ig_eq)

# NOTE: Convert the same string when direct config inspection is needed.
parsed_config = thermo_source_hub_config_from_str(thermo_source_hub_config)
cp_ig_source_type = parsed_config["Cp_IG"].property_source
if cp_ig_source_type is not None:
    direct_cp_ig_values = thermo_source_hub.get_comp_values(
        source_type=cp_ig_source_type,
        symbol="Cp_IG",
        components=components,
    )
    print("[bold]Direct Cp_IG numeric values in component order[/bold]")
    print(direct_cp_ig_values)

# NOTE: R is configured as a model-source constant.
r_src = thermo_source_registry["R"]["src"]
print("[bold]R constant source selected by registry[/bold]")
print(r_src)
print("[bold]R constant value[/bold]")
print(r_src.value)

# NOTE: alpha is configured as model-source matrix data.
alpha_src = thermo_source_registry["alpha"]["src"]
print("[bold]alpha matrix source selected by registry[/bold]")
print(alpha_src)
for mixture_id, matrix_source in alpha_src.items():
    print("[bold]alpha matrix value[/bold]", mixture_id)
    print(matrix_source.matX(
        components=mixture_1,
        symbol_format="alphabetic",
        component_key="Name",
        mixture_key="Name",
    ))

# NOTE: CUSTOM_MATRIX is configured as custom-source matrix data.
custom_matrix_src: Any = thermo_source_registry["CUSTOM_MATRIX"]["src"]
print("[bold]CUSTOM_MATRIX source selected by registry[/bold]")
print(custom_matrix_src)
print("[bold]CUSTOM_MATRIX raw value[/bold]")
print(custom_matrix_src.value)
