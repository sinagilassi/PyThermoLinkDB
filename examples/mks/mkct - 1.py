# import packages/modules
from pyThermoLinkDB import mkct, ConstantsSourceCore
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from rich import print
import sys
from pathlib import Path
# ! model source
from examples.model_source_2 import model_source

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# MODEL SOURCE
# =======================================
constantssource = model_source.constants_source
constants_symbols = model_source.constants_symbols

print(constantssource)
print(constants_symbols)

# =======================================
# MAKE CONSTANTS SOURCE DIRECTLY
# =======================================
constants_src: ConstantsSourceCore | None = mkct(
    model_source=model_source,
)

# print
print(constants_src)

# >> check
if constants_src is None:
    raise ValueError("Failed to create constants source.")

# results
# ! all constants
print(constants_src.constants)
print(constants_src.all_constants())

# ! all constant symbols
print(constants_src.constants_symbols)
print(constants_src.props_symbols)

# ! available constants
print(constants_src.is_constant_available('R'))
print(constants_src.is_constant_available('Unknown_Constant'))

# ! check a list of constants
print(constants_src.check_constants_availability(['R', 'dH_rxn']))
print(constants_src.check_props_availability(['R', 'Unknown_Constant']))

# ! all constants available
print(constants_src.all_constants_available(['R', 'dH_rxn']))
print(constants_src.all_constants_available(
    ['R', 'dH_rxn', 'Unknown_Constant'])
)

# ! specific constants
# NOTE: raw constant entry, works for any constant value shape
print(constants_src.constant(name='R'))
print(constants_src.const(name='R'))

# NOTE: symbol metadata
print(constants_src.symbol(name='R'))
print(constants_src.const_symbol(name='R'))

# NOTE: property-like constant, works when the constant entry has
# value/unit/symbol fields
print(constants_src.prop(name='R'))
print(constants_src.select_scalar(symbol='R'))
print(constants_src.select(symbol='dH_rxn'))

# NOTE: constants may also be nested dictionaries, lists, or any other source
# value. Use constant()/const() for those raw values.
print(constants_src.constant(name='dH_rxn'))

# NOTE: select wise
# ! select wise
print(constants_src.select(symbol='R'))
print(constants_src.select(symbol='C1'))
print(constants_src.select(symbol='Cp_IG'))
print(constants_src.select(symbol='dH_rxn'))
print(constants_src.select(symbol='Xb'))
print(constants_src.select(symbol='X'))
print(constants_src.select(symbol='Unknown_Constant'))
