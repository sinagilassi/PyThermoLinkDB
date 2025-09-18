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
    'carbon dioxide-g.pkl'
)
# load
CO2_thermodb = ptdb.load_thermodb(CO2_thermodb_file)
print(type(CO2_thermodb))

# check
print(CO2_thermodb.check())

# SECTION 🧪 methanol
# thermodb file name
MeOH_thermodb_file = os.path.join(
    thermodb_dir,
    'methanol-g.pkl'
)

print(f"thermodb file: {MeOH_thermodb_file}")
# load
MeOH_thermodb = ptdb.load_thermodb(MeOH_thermodb_file)
print(type(MeOH_thermodb))

# check
print(MeOH_thermodb.check())

# SECTION 🧪 toluene
# thermodb file name
benzene_thermodb_file = os.path.join(
    thermodb_dir,
    'benzene-l.pkl'
)

print(f"thermodb file: {benzene_thermodb_file}")
# load
C6H6_thermodb = ptdb.load_thermodb(benzene_thermodb_file)
print(type(C6H6_thermodb))

# check
print(C6H6_thermodb.check())

# =======================================
# 🛠️ INIT THERMODB HUB
# =======================================
# init thermodb hub
thub1 = ptdblink.init()
print(type(thub1))

# add component thermodb
thub1.add_thermodb('MeOH', MeOH_thermodb)
thub1.add_thermodb('CO2', CO2_thermodb)
thub1.add_thermodb('C6H6', C6H6_thermodb)

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
dt2_ = datasource['MeOH']['Tc']
print(type(dt2_))
print(dt2_)

# CO2 equation
eq1_ = equationsource['CO2']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))
