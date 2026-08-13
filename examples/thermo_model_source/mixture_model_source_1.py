# import libs
import os
from typing import List
from rich import print
import pyThermoLinkDB as ptldb
from pyThermoLinkDB import build_model_source, build_mixture_model_source
from pyThermoLinkDB.models import ModelSource, MixtureModelSource
import pyThermoDB as ptdb
from pythermodb_settings.models import Component
from pyThermoDB import (
    MixtureThermoDB,
    build_mixture_thermodb_from_reference,
)

# ! components
from examples.thermo_model_source.components_1 import C2H4, C2H6, CO2, C2H5OH, CH3OH, CH4
# ! reference content
from examples.reference_2 import REFERENCE_CONTENT

# check version
print(ptldb.__version__)
print(ptdb.__version__)


# ====================================
# ☑️ SET COMPONENTS
# ====================================
# ! mixture
binary_mixture_components = [CH3OH, C2H5OH]
ternary_mixture_components = [CH3OH, C2H5OH, CH4]
# >> methanol-ethanol
# >> methanol-methane
# >> ethanol-methane
# mixture_names: List[str] = ['methanol|ethanol', 'methanol|methane']

# ====================================
# ☑️ BUILD MIXTURE THERMODB
# ====================================
# SECTION: build component thermodb
# ! mixture thermodb
mixture_thermodb_: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
    components=binary_mixture_components,
    reference_content=REFERENCE_CONTENT,
)
print(f"mixture_thermodb_:")
print(mixture_thermodb_)
# >> check
if mixture_thermodb_ is None:
    raise ValueError("mixture_thermodb_ is None")

# ====================================
# ☑️ BUILD MIXTURE MODEL SOURCE
# ====================================
# NOTE: build mixture model source
mixture_model_source: MixtureModelSource = build_mixture_model_source(
    mixture_thermodb=mixture_thermodb_,
    mixture_keys=['Name-State', 'Formula-State'],
    mixture_custom_ids=['custom-mixture-id-1', 'custom-mixture-id-2'],
)
print(f"mixture_model_source:")
print(mixture_model_source)

# # SECTION: build model source
# model_source: ModelSource = build_model_source(
#     source=[mixture_model_source],
# )
# print(f"model_source:")
# print(model_source)

# # ====================================
# # ☑️ ACCESS MIXTURE MODEL SOURCE
# # ====================================
# # NOTE: access a
# # inspect what mixtures are available
# print(model_source.data_source.keys())
# print(model_source.equation_source.keys())

# # access one mixture by its mixture id
# # names are sorted inside build_mixture_model_source()
# mixture_id = "ethanol|methanol"
# mixture_data = model_source.data_source[mixture_id]
# mixture_equations = model_source.equation_source[mixture_id]

# print(mixture_data.keys())
# print(mixture_equations.keys())
