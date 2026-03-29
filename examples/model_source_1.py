# import packages/modules
import os
from rich import print
from typing import Callable, Dict, Optional, Union, List, Any
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import (
    build_component_model_source,
    build_components_model_source,
    build_model_source
)
from pyThermoLinkDB.models import ComponentModelSource, ModelSource
from pythermodb_settings.models import Component, Pressure, Temperature, CustomProp, Volume, CustomProperty
from pyThermoDB import ComponentThermoDB
from pyThermoDB import build_component_thermodb_from_reference
# locals
from examples.reference import REFERENCE_CONTENT

# check version
print(ptdb.__version__)
print(ptdblink.__version__)

# ====================================================
# SECTION: BUILD COMPONENT THERMODB
# ====================================================
# NOTE: parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(parent_dir)

# NOTE: thermodb directory
thermodb_dir = os.path.join(parent_dir, 'thermodb')
print(thermodb_dir)

# NOTE: create component
# ! propane
# carbon dioxide
CO2 = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g',
    X={
        "name": "mole",
        "value": 1,
        "unit": "mol",
        "symbol": "n"
    }
)

# Hydrogen
H2 = Component(
    name='hydrogen',
    formula='H2',
    state='g',
    X={
        "name": "mole",
        "value": 3,
        "unit": "mol",
        "symbol": "n"
    }
)

# methanol
CH3OH = Component(
    name='methanol',
    formula='CH3OH',
    state='g',
    X={
        "name": "mole",
        "value": 0,
        "unit": "mol",
        "symbol": "n"
    }
)

# ethanol
C2H5OH = Component(
    name='ethanol',
    formula='C2H5OH',
    state='g',
    X={
        "name": "mole",
        "value": 0,
        "unit": "mol",
        "symbol": "n"
    }
)

# water
H2O = Component(
    name='water',
    formula='H2O',
    state='g',
    X={
        "name": "mole",
        "value": 0,
        "unit": "mol",
        "symbol": "n"
    }
)

# Carbon monoxide
CO = Component(
    name='carbon monoxide',
    formula='CO',
    state='g',
    X={
        "name": "mole",
        "value": 0,
        "unit": "mol",
        "symbol": "n"
    }
)

# ethylene
C2H4 = Component(
    name='ethylene',
    formula='C2H4',
    state='g',
    X={
        "name": "mole",
        "value": 1,
        "unit": "mol",
        "symbol": "n"
    }
)

# ethane
C2H6 = Component(
    name='ethane',
    formula='C2H6',
    state='g',
    X={
        "name": "mole",
        "value": 0,
        "unit": "mol",
        "symbol": "n"
    }
)

# components
components = [CO2, C2H5OH]

# NOTE: ignore state properties
ignore_state_props = ['MW', 'VaPr', 'Cp_IG']

# ====================================================
# SECTION: build components thermodb
# ====================================================
thermodb_components: List[ComponentThermoDB] = []

for comp in components:
    thermodb_component = build_component_thermodb_from_reference(
        component_name=comp.name,
        component_formula=comp.formula,
        component_state=comp.state,
        reference_content=REFERENCE_CONTENT,
        ignore_state_props=ignore_state_props,
    )
    if thermodb_component is None:
        raise ValueError(f"thermodb_component for {comp.name} is None")
    thermodb_components.append(thermodb_component)

# ====================================================
# SECTION: build model source
# ====================================================
# NOTE: with partially matched rules
component_model_source: List[ComponentModelSource] = build_components_model_source(
    components_thermodb=thermodb_components,
    rules=None,
)

# model source
model_source: ModelSource = build_model_source(
    source=component_model_source,
)
# ====================================================
# SECTION: THERMODB LINK CONFIGURATION
# ====================================================

# build datasource & equationsource
datasource = model_source.data_source
equationsource = model_source.equation_source

# ====================================================
# SECTION: model source
# ====================================================
model_source: ModelSource = ModelSource(
    data_source=datasource,
    equation_source=equationsource
)
