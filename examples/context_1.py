# import packages/modules
from rich import print
from typing import Dict
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import load_and_build_model_source
from pyThermoLinkDB.models import ModelSource
import pyThermoDB as ptdb
from pythermodb_settings.models import (
    Component,
    ComponentRule,
    ComponentThermoDBSource,
    CustomProperty
)
from pyThermoLinkDB.thermo import mkdt, mkeq, mkeqs, EquationSourceCore, DataSourceCore, Context
# ! model source
from examples.model_source_1 import model_source, CO2, C2H5OH

# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# CONTEXT
# =======================================
# NOTE: build context
ctx = Context(
    model_source=model_source,
    component_key='Name-State'
)

# NOTE: constant & variable pools
constants = {
    'R': {
        'symbol': 'R',
        'value': 8.314462618,
        'unit': 'J/mol.K'
    },
    'T_ref': {
        'symbol': 'T_ref',
        'value': 298.15,
        'unit': 'K'
    }
}

# NOTE: add bulk data to pool
res_ = ctx.add_bulk_to_pool(constants)
print(res_)

# pool
print(ctx.pools)
