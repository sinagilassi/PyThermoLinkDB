# import packages/modules
from typing import Dict, Optional
import os
from rich import print
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB.models import ModelSource
import pyThermoDB as ptdb

# check version
print(ptdblink.__version__)
print(ptdb.__version__)
# author
print(ptdblink.__author__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================
# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current dir: {current_dir}")

# SECTION CO2
_thermodb_file = os.path.join(
    current_dir,
    'thermodb',
    'Methane-1.pkl'
)

# NOTE: load
_thermodb = ptdb.load_thermodb(_thermodb_file)
print(type(_thermodb))

# check
print(_thermodb.check())

# =======================================
# 🛠️ INIT THERMODB HUB
# =======================================
# init thermodb hub
thub1 = ptdblink.init()
print(type(thub1))

# NOTE: add thermodb with thermodb rule
# update thermodb rule
thermodb_rule_: Dict[str, Dict[str, str]] = {
    'DATA': {
        'critical-pressure': 'Pc',
        'critical-temperature': 'Tc',
        'acentric-factor': 'AcFa'
    },
    'EQUATIONS': {
        'vapor-pressure': 'VaPr',
        'heat-capacity': 'Cp_IG'
    }
}
# add
thub1.add_thermodb(
    'CH4',
    _thermodb,
    rules=thermodb_rule_
)

# get components
print(thub1.items())

# check
res_ = thub1.thermodb_rule
print(res_)

# =======================================
# 🏗️ BUILD
# =======================================
# ! old method
datasource, equationsource = thub1.build()
print(datasource)
print(equationsource)

# ! new method
model_source: ModelSource = thub1.build_model_source()
print(model_source)

# ! hub
print(thub1.hub)

# =======================================
# ✅ TEST
# =======================================
# data
dt1_ = datasource['CH4']['Pc']
print(type(dt1_))
print(dt1_)

# equation
eq1_ = equationsource['CH4']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))
