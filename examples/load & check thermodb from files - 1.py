# import packages/modules
import os
from rich import print
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb

# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"parent directory: {parent_dir}")
# thermodb directory
thermodb_dir = os.path.join(parent_dir, 'thermodb')
print(f"thermodb directory: {thermodb_dir}")

# SECTION CO2
CO2_thermodb_file = os.path.join(
    thermodb_dir,
    'carbon dioxide.pkl'
)
# load
CO2_thermodb = ptdb.load_thermodb(CO2_thermodb_file)
print(type(CO2_thermodb))

# check
print(CO2_thermodb.check())

# SECTION 🧪 ethanol
# thermodb file name
EtOH_thermodb_file = os.path.join(
    thermodb_dir,
    'ethanol.pkl'
)

print(f"thermodb file: {EtOH_thermodb_file}")
# load
EtOH_thermodb = ptdb.load_thermodb(EtOH_thermodb_file)
print(type(EtOH_thermodb))

# check
print(EtOH_thermodb.check())

# SECTION 🧪 water
# thermodb file name
H2O_thermodb_file = os.path.join(
    thermodb_dir,
    'water.pkl'
)

print(f"thermodb file: {H2O_thermodb_file}")
# load
H2O_thermodb = ptdb.load_thermodb(H2O_thermodb_file)
print(type(H2O_thermodb))

# check
print(H2O_thermodb.check())

# =======================================
# 🛠️ INIT THERMODB HUB
# =======================================
# init thermodb hub
thub1 = ptdblink.init()
print(type(thub1))

# add component thermodb
# thub1.add_thermodb('EtOH', EtOH_thermodb)
thub1.add_thermodb('CO2', CO2_thermodb)
# thub1.add_thermodb('H2O', H2O_thermodb)
# get components
print(thub1.items())

# =======================================
# ⚙️ THERMODB LINK CONFIGURATION
# =======================================
# add thermodb rule
# define thermodb rule
thermodb_config_file = os.path.join(parent_dir, 'thermodb_config.yml')
print(f"thermodb config file: {thermodb_config_file}")

# all components
res_ = thub1.config_thermodb_rule(thermodb_config_file)
print(res_)

# =======================================
# 🏗️ BUILD
# =======================================
datasource, equationsource = thub1.build()
print(datasource)
print(equationsource)

# hub
print(thub1.hub)

# check
print(thub1.check())

# =======================================
# ✅ TEST
# =======================================
# CO2 data
dt1_ = datasource['CO2']['Pc']
print(type(dt1_))
print(dt1_)

# MeOH data
# dt2_ = datasource['MeOH']['Tc']
# print(type(dt2_))
# print(dt2_)

# CO2 equation
eq1_ = equationsource['CO2']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))
