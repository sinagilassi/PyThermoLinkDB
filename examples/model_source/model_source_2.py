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
from examples.reference_2 import REFERENCE_CONTENT

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

# ! define custom rules
thermodb_rules: Dict[str, Dict[str, ComponentRule]] = {
    'ALL': {
        'CONSTANTS': {
            'Universal Gas Constant': 'R',
            'Constant1': 'C1',
            'total heat capacity of ideal gas': 'Cp_IG',
            'enthalpy of reaction': 'dH_rxn',
            'binary parameter': 'Xb',
            'custom constants': 'X'
        }
    },
    'CUSTOM-REF-1::Custom-Constants': {
        'CONSTANTS': {
            'Universal Gas Constant': 'R',
            'Constant1': 'C1',
        }
    },
    'CUSTOM-REF-1::Custom-Constants-2': {
        'CONSTANTS': {
            'total heat capacity of ideal gas': 'Cp_IG',
            'enthalpy of reaction': 'dH_rxn',
        }
    }

}
# ! with rules
constants_model_source_with_rules: ConstantsModelSource = build_constants_model_source(
    constants_thermodb=constants_thermodb,
    rules=thermodb_rules
)
# >> log
print(constants_model_source_with_rules)

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

# ! with rules
sources_with_rules: list = [
    constants_model_source_with_rules
] + component_model_source

# model source
model_source_with_rules: ModelSource = build_model_source(
    source=sources_with_rules,
)
# >> log
print(model_source_with_rules)

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
