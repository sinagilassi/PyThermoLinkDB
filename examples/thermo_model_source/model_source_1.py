# import packages/modules
import os
from rich import print
from typing import Callable, Dict, Optional, Union, List, Any
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import (
    build_component_model_source,
    build_components_model_source,
    build_constants_model_source,
    build_model_source
)
from pyThermoLinkDB.models import ComponentModelSource, ModelSource, ConstantsModelSource
from pythermodb_settings.models import Component, Pressure, Temperature, CustomProp, Volume, CustomProperty, ComponentRule
from pyThermoDB import ComponentThermoDB, ConstantsThermoDB
from pyThermoDB import (
    build_component_thermodb_from_reference,
    build_constants_thermodb_from_reference
)
# locals
# ! components
from examples.thermo_model_source.components_1 import components
# ! reference content
from examples.reference_2 import REFERENCE_CONTENT

# check version
print(ptdb.__version__)
print(ptdblink.__version__)


# NOTE: ignore state properties
ignore_state_props = ['MW', 'VaPr', 'Cp_IG', 'Cp_LIQ']

# ====================================================
# SECTION: build components thermodb
# ====================================================
thermodb_components: List[ComponentThermoDB] = []

for comp in components:
    thermodb_component: ComponentThermoDB | None = build_component_thermodb_from_reference(
        component_name=comp.name,
        component_formula=comp.formula,
        component_state=comp.state,
        reference_content=REFERENCE_CONTENT,
        ignore_state_props=ignore_state_props,
    )
    if thermodb_component is None:
        raise ValueError(f"thermodb_component for {comp.name} is None")

    # log
    print(thermodb_component)
    thermodb_components.append(thermodb_component)


# NOTE: with partially matched rules
component_model_source: List[ComponentModelSource] = build_components_model_source(
    components_thermodb=thermodb_components,
    rules=None,
)
print(component_model_source)

# ====================================================
# SECTION: build constants thermodb
# ====================================================
# NOTE: build constants thermodb from reference
constants_thermodb: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=REFERENCE_CONTENT,
)
# >> check
if constants_thermodb is None:
    raise ValueError("constants_thermodb is None")
# log
print(constants_thermodb)

# NOTE: build model source with constants thermodb
# ! no rules
constants_model_source: ConstantsModelSource = build_constants_model_source(
    constants_thermodb=constants_thermodb,
    rules=None,
)
# >> log
print(constants_model_source)

# ====================================================
# SECTION: build model source
# ====================================================
# NOTE: all model source
# ! with rules
sources: list = [constants_model_source] + component_model_source

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
