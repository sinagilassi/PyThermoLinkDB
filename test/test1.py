# import packages/modules
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb
import os
from pprint import pprint as pp

# local

# check version
print(ptdblink.__version__)
print(ptdb.__version__)
# author
print(ptdblink.__author__)

# =======================================
# ! LOAD THERMODB
# =======================================

# ! ethanol
# thermodb file name
EtOH_thermodb_file = os.path.join(os.getcwd(), 'test', 'ethanol.pkl')
# load
EtOH_thermodb = ptdb.load_thermodb(EtOH_thermodb_file)
print(type(EtOH_thermodb))

EtOH_thermodb

# check
pp(EtOH_thermodb.check())
# check properties
pp(EtOH_thermodb.check_properties())
# datastrcuture
pp(EtOH_thermodb.check_property('GENERAL').data_structure())

# ! methanol
# thermodb file name
MeOH_thermodb_file = os.path.join(os.getcwd(), 'test', 'methanol.pkl')
# load
MeOH_thermodb = ptdb.load_thermodb(MeOH_thermodb_file)
print(type(MeOH_thermodb))

MeOH_thermodb

# check
pp(MeOH_thermodb.check())

# ! CO2
CO2_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'Carbon Dioxide-multiple.pkl')
# load
CO2_thermodb = ptdb.load_thermodb(CO2_thermodb_file)
print(type(CO2_thermodb))

# check
pp(CO2_thermodb.check())
pp(CO2_thermodb.check_property('GENERAL').data_structure())
pp(CO2_thermodb.check_property('GENERAL-2').data_structure())

# =======================================
# ! THERMODB LINK CONFIGURATION
# =======================================
# init thermodb hub
thub1 = ptdblink.thermodb_hub()
print(type(thub1))

# add component thermodb
thub1.add_thermodb('EtOH', EtOH_thermodb)
thub1.add_thermodb('MeOH', MeOH_thermodb)
thub1.add_thermodb('CO2', CO2_thermodb)

# * add thermodb rule
thermodb_config_file = os.path.join(os.getcwd(), 'test', 'thermodb_config.yml')
# one component
# thub1.config_thermodb_rule(thermodb_config_file, name='EtOH')
# all components
thub1.config_thermodb_rule(thermodb_config_file, name='ALL')

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
pp(datasource['CO2']['Pc']['value'])

# equation
pp(equationsource['CO2']['VaPr'].args)
pp(equationsource['CO2']['VaPr'].cal(T=298.15))
