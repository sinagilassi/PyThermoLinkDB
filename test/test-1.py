# import packages/modules
import os
from rich import print
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb

# check version
print(ptdblink.__version__)
print(ptdb.__version__)
# author
print(ptdblink.__author__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================

# SECTION CO2
CO2_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'carbon dioxide-1.pkl')
# load
CO2_thermodb = ptdb.load_thermodb(CO2_thermodb_file)
print(type(CO2_thermodb))

# check
print(CO2_thermodb.check())

# SECTION 🧪 methanol
# thermodb file name
MeOH_thermodb_file = os.path.join(os.getcwd(), 'test', 'methanol-1.pkl')
print(f"thermodb file: {MeOH_thermodb_file}")
# load
MeOH_thermodb = ptdb.load_thermodb(MeOH_thermodb_file)
print(type(MeOH_thermodb))

MeOH_thermodb

# check
print(MeOH_thermodb.check())

# SECTION 🧪 toluene
# thermodb file name
toluene_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'toluene-1.pkl')
print(f"thermodb file: {toluene_thermodb_file}")
# load
toluene_thermodb = ptdb.load_thermodb(toluene_thermodb_file)
print(type(toluene_thermodb))

# SECTION 🔬 nrtl
# thermodb file name
nrtl_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'thermodb_nrtl_1.pkl')
print(f"thermodb file: {nrtl_thermodb_file}")
# load
nrtl_thermodb = ptdb.load_thermodb(nrtl_thermodb_file)
print(type(nrtl_thermodb))

# check
print(nrtl_thermodb.check())

# =======================================
# 🛠️ INIT THERMODB HUB
# =======================================
# init thermodb hub
thub1 = ptdblink.init()
print(type(thub1))

# add component thermodb
thub1.add_thermodb('MeOH', MeOH_thermodb)
thub1.add_thermodb('CO2', CO2_thermodb)
thub1.add_thermodb('toluene', toluene_thermodb)
# matrix data
thub1.add_thermodb('NRTL', nrtl_thermodb)

# get components
print(thub1.items())

# =======================================
# ⚙️ THERMODB LINK CONFIGURATION
# =======================================
# add thermodb rule
# define thermodb rule
thermodb_config_file = os.path.join(os.getcwd(), 'test', 'thermodb_config.yml')

# no change
# thermodb_config_file = os.path.join(os.getcwd(), 'test', 'thermodb_config_2.yml')

# all components
res_ = thub1.config_thermodb_rule(thermodb_config_file)
# selected components
# res_ = thub1.config_thermodb_rule(thermodb_config_file, names=["MeOH", "CO2"])
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

# NRTL data
dt3_ = datasource['NRTL']['alpha_i_j']
print(type(dt3_))
print(dt3_.ij("Alpha_methanol_ethanol"))

# CO2 equation
eq1_ = equationsource['CO2']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))

# nrtl equation
eq2_ = equationsource['NRTL']['tau_i_j']
print(type(eq2_))
print(eq2_)
print(eq2_.args)
print(eq2_.cal(T=298.15))
