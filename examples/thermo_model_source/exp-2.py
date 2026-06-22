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
    from examples.model_source_2 import CO2, C2H5OH, model_source, components


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

# NOTE: components configuration
component_key = 'Name-State'

# =======================================
# â˜‘ï¸ BUILD MODEL SOURCE
# =======================================
# NOTE: thermo data, equations, and constants to be extracted from the model source
requested_data = ['EnFo_IG', 'Tc', 'Pc']
requested_equations = ['Cp_IG', 'VaPr']
requested_constants = ['R', 'dH_rxn']

# NOTE: build thermo model source
thermo_model_src: ThermoModelSource | None = build_thermo_model_source(
    model_source=model_source,
    components=components,
    component_key=component_key,
    requested_data=requested_data,
    requested_equations=requested_equations,
    requested_constants=requested_constants,
    description="Example thermo model source with rules",
    mode='log'  # options: 'silent', 'log', 'attach'
)

if thermo_model_src is None:
    raise RuntimeError("Failed to build thermo model source.")


print("\n[bold green]Thermo model source[/bold green]")
print(thermo_model_src.thermo_src)

# =======================================
# â˜‘ï¸ BUILD MODEL SOURCE (no configuration)
# =======================================
# NOTE: build thermo model source
thermo_model_src: ThermoModelSource | None = build_thermo_model_source(
    model_source=model_source,
    components=components,
    component_key=component_key,
    description="Example thermo model source with rules",
    mode='log'  # options: 'silent', 'log', 'attach'
)

if thermo_model_src is None:
    raise RuntimeError("Failed to build thermo model source.")


print("\n[bold green]Thermo model source[/bold green]")
print(thermo_model_src.thermo_src)
