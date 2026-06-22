import pyThermoLinkDB as ptdblink
from pyThermoLinkDB.utils.input_builder import validate_and_build_inputs
from pyThermoLinkDB.builders import build_thermo_model_source, ThermoModelSource
import pyThermoDB as ptdb
from pathlib import Path
import contextlib
import io
import logging
import sys
import pycuc
from rich import print

from rich.console import Console

console = Console(force_terminal=True, color_system="truecolor")
print = console.print

# ! from pyThermoLinkDB

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# import packages/modules
# ! from pyThermoLinkDB

# ! model source & components
logging.getLogger("pyThermoLinkDB.docs.thermolink").setLevel(logging.ERROR)
with contextlib.redirect_stdout(io.StringIO()):
    from examples.model_source_2 import CO2, C2H5OH, model_source_with_rules


# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# âœ… unit conversion settings
# =======================================
# NOTE: create unit conversion function using pycuc
unit_conversion_fn = pycuc.convert_from_to

# NOTE: create unit availability function using pycuc
unit_availability_fn = pycuc.is_unit_available

# =======================================
# âœ… inputs
# =======================================
# NOTE: universal inputs
runtime_inputs = {
    "T": {"value": 25.0, "unit": "C"},
    "P": {"value": 101325.0, "unit": "Pa"},
    "Tc": {"value": 302.0, "unit": "K"},
}

runtime_inputs_symbols = list(runtime_inputs.keys())


# =======================================
# BUILD MODEL SOURCE
# =======================================
# NOTE: components configuration
components = [CO2, C2H5OH]
component_key = 'Name-State'

# NOTE: thermo data, equations, and constants to be extracted from the model source
requested_data = ['EnFo_IG', 'Tc', 'Pc']
requested_equations = ['Cp_IG', 'VaPr']
requested_constants = ['R', 'dH_rxn']

# NOTE: build thermo model source
thermo_model_src: ThermoModelSource | None = build_thermo_model_source(
    model_source=model_source_with_rules,
    components=components,
    component_key=component_key,
    requested_data=requested_data,
    requested_equations=requested_equations,
    requested_constants=requested_constants
)

if thermo_model_src is None:
    raise RuntimeError("Failed to build thermo model source.")


def show_thermo_data(symbols: list[str]) -> None:
    print("\n[bold green]Thermo data[/bold green]")
    for symbol in symbols:
        data_sources = getattr(thermo_model_src, f"{symbol}_src", {})
        values = getattr(thermo_model_src, f"{symbol}_value", None)

        print(f"\n[bold cyan]{symbol}[/bold cyan]")
        print("values =", values)
        for component_id, prop in data_sources.items():
            print(
                component_id,
                {
                    "value": prop.value,
                    "unit": prop.unit,
                    "symbol": prop.symbol,
                }
            )


def show_thermo_constants(symbols: list[str]) -> None:
    print("\n[bold green]Thermo constants[/bold green]")
    for symbol in symbols:
        const_source = getattr(thermo_model_src, f"{symbol}_src", None)
        const_value = getattr(thermo_model_src, f"{symbol}_value", None)

        print(f"\n[bold cyan]{symbol}[/bold cyan]")
        print("value =", const_value)
        if const_source is not None:
            print(
                "source =",
                {
                    "value": const_source.value,
                    "unit": const_source.unit,
                    "symbol": const_source.symbol,
                }
            )


def show_dynamic_attribute_group(symbols: list[str]) -> None:
    for symbol in symbols:
        print(f"\n[bold cyan]{symbol}[/bold cyan]")
        for suffix in ("src", "comp", "value", "eq"):
            attr_name = f"{symbol}_{suffix}"
            print(f"{attr_name} =", getattr(thermo_model_src, attr_name, None))


show_thermo_data(requested_data)
show_thermo_constants(requested_constants)

print("\n[bold green]Thermo model source dynamic attributes[/bold green]")
show_dynamic_attribute_group(requested_data)
show_dynamic_attribute_group(requested_equations)
show_dynamic_attribute_group(requested_constants)

print("\n[bold green]Sample equation calculations with validated runtime inputs[/bold green]")
for equation_symbol in requested_equations:
    eq_sources = getattr(thermo_model_src, f"{equation_symbol}_eq", {})
    print(f"\n[bold cyan]{equation_symbol}[/bold cyan]")
    for component_id, equation_source in eq_sources.items():
        # ! validate and build inputs for the equation source
        input_args = validate_and_build_inputs(
            equation_source.inputs,
            runtime_inputs,
            unit_conversion_fn=unit_conversion_fn,
            unit_availability_fn=unit_availability_fn
        )
        print(component_id, "input_args =", input_args)

        # ! calculate the equation source with the built input arguments
        result = equation_source.calc(**input_args)
        print(component_id, result)
