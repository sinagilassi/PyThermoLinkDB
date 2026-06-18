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
# ✅ unit conversion settings
# =======================================
# NOTE: create unit conversion function using pycuc
unit_conversion_fn = pycuc.convert_from_to

# NOTE: create unit availability function using pycuc
unit_availability_fn = pycuc.is_unit_available

# =======================================
# ✅ inputs
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
thermo_data = ['EnFo_IG', 'Tc', 'Pc']
thermo_equations = ['Cp_IG', 'VaPr']
thermo_constants = ['R', 'dH_rxn']

# NOTE: build thermo model source
thermo_model_src: ThermoModelSource | None = build_thermo_model_source(
    model_source=model_source_with_rules,
    components=components,
    component_key=component_key,
    thermo_data=thermo_data,
    thermo_equations=thermo_equations,
    thermo_constants=thermo_constants,
    description="Example thermo model source with rules",
    mode='log'  # options: 'silent', 'log', 'attach'
)

if thermo_model_src is None:
    raise RuntimeError("Failed to build thermo model source.")


dynamic_attrs = thermo_model_src.dynamic_attributes()

print("\n[bold green]Thermo model source dynamic attributes[/bold green]")
print(dynamic_attrs)
