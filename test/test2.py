# import packages/modules
import os
from rich import print as pp
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb

# local

# check version
print(ptdblink.__version__)
print(ptdb.__version__)
# author
print(ptdblink.__author__)

# =======================================
# ! LOAD THERMODB
# =======================================

# SECTION CO2
CO2_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'carbon dioxide-1.pkl')
# load
CO2_thermodb = ptdb.load_thermodb(CO2_thermodb_file)
print(type(CO2_thermodb))

# check
pp(CO2_thermodb.check())

# SECTION methanol
# thermodb file name
MeOH_thermodb_file = os.path.join(os.getcwd(), 'test', 'methanol-1.pkl')
print(f"thermodb file: {MeOH_thermodb_file}")
# load
MeOH_thermodb = ptdb.load_thermodb(MeOH_thermodb_file)
print(type(MeOH_thermodb))

MeOH_thermodb

# check
pp(MeOH_thermodb.check())

# SECTION nrtl
# thermodb file name
nrtl_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'thermodb_nrtl_1.pkl')
print(f"thermodb file: {nrtl_thermodb_file}")
# load
nrtl_thermodb = ptdb.load_thermodb(nrtl_thermodb_file)
print(type(nrtl_thermodb))

# check
pp(nrtl_thermodb.check())

# =======================================
# ! THERMODB LINK CONFIGURATION
# =======================================
# init thermodb hub
thub1 = ptdblink.init()
print(type(thub1))

# add component thermodb
thub1.add_thermodb('MeOH', MeOH_thermodb)
thub1.add_thermodb('CO2', CO2_thermodb)
# matrix data
thub1.add_thermodb('NRTL', nrtl_thermodb)

# * add thermodb rule
thermodb_config_file = os.path.join(os.getcwd(), 'test', 'thermodb_config.yml')
# one component
# thub1.config_thermodb_rule(thermodb_config_file, name='EtOH')
# all components
thub1.config_thermodb_rule(thermodb_config_file, name='ALL')
# selected components
# thub1.config_thermodb_rule(thermodb_config_file, name='MeOH')
# thub1.config_thermodb_rule(thermodb_config_file, name='CO2')

# thermodb
# pp(thub1.thermodb)

# thermodb rules
# pp(thub1.thermodb_rule)

# get components
pp(thub1.get_components())

# build
datasource, equationsource = thub1.build()
pp(datasource)
pp(equationsource)

# hub
pp(thub1.hub)

# check
# pp(thub1.check())

# =======================================
# ! TEST
# =======================================
# data
dt1_ = datasource['CO2']['Pc']
pp(type(dt1_))
pp(dt1_['data']['value'])
pp(dt1_['data']['unit'])
pp(dt1_['source'])

# matrix data
dt2_ = datasource['NRTL']['Alpha_i_j']
pp(type(dt2_))
pp(dt2_['data'])
pp(dt2_['data'])
# pp(dt2_['source'].get_matrix_property("Alpha_i_j", ['methanol', 'ethanol']))
pp(dt2_['source'](['methanol', 'ethanol']))

# equation
pp(equationsource['CO2']['VaPr'].args)
pp(equationsource['CO2']['VaPr'].cal(T=298.15))

# nrtl equation
pp(equationsource['NRTL']['tau_i_j'].args)
pp(equationsource['NRTL']['tau_i_j'].cal(T=298.15))
