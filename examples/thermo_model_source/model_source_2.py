# import packages/modules
import os
from rich import print
from typing import Callable, Dict, Optional, Union, List, Any
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import (
    build_model_source
)
from pyThermoLinkDB.models import ModelSource
# locals
# ! components
from examples.thermo_model_source.components_1 import *
# ! component model source
from examples.thermo_model_source.component_model_source_1 import (
    component_model_source,
    constants_model_source
)
# ! mixture model source
from examples.thermo_model_source.mixture_model_source_1 import mixture_model_source

# check version
print(ptdb.__version__)
print(ptdblink.__version__)

# ====================================================
# SECTION: build model source
# ====================================================
# NOTE: all model source
# ! contain all model source: constants, components, mixture
sources: list = [constants_model_source] + \
    component_model_source + [mixture_model_source]

# model source
model_source: ModelSource = build_model_source(
    source=sources,
)
# >> log
print(model_source)

# ====================================================
# SECTION: THERMODB LINK CONFIGURATION
# ====================================================

# build datasource & equationsource
datasource = model_source.data_source
equationsource = model_source.equation_source
constantssource = model_source.constants_source
# symbols
data_symbols = model_source.data_symbols
equation_symbols = model_source.equation_symbols
constants_symbols = model_source.constants_symbols
