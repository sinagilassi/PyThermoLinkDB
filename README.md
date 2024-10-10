# PyThermoLinkDB

![Downloads](https://img.shields.io/pypi/dm/PyThermoLinkDB) ![PyPI](https://img.shields.io/pypi/v/PyThermoLinkDB) ![Python Version](https://img.shields.io/pypi/pyversions/PyThermoLinkDB.svg) ![License](https://img.shields.io/pypi/l/PyThermoLinkDB)

PyThermoLinkDB is a Python package providing a robust and efficient interface between `PyThermoDB` and other applications. It enables seamless thermodynamic data exchange, integration, and analysis. With PyThermoLinkDB, developers can easily link PyThermoDB to various tools, frameworks, and databases, streamlining thermodynamic workflows.

**Key Features:**

-   Simple and intuitive API
-   Efficient data transfer and integration
-   Compatible with multiple data formats
-   Extensive documentation and examples

Ideal for researchers, engineers, and developers working with thermodynamic data, PyThermoLinkDB simplifies data integration and analysis, accelerating scientific discoveries and industrial applications.

## Google Colab

You can run `PyThermoLinkDB` in Google Colab:

| Version | Scripts |
|---------|---------|
| 1.0.0 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1JU1ljkHgKcBNe_CuSh2Bg7hoKwQUJti0?usp=sharing) |

## Installation

Install pyThermoLinkDB with pip

```python
import pyThermoLinkDB as ptdblink
# check version
print(ptdblink.__version__)
```

## Usage Example

```python
# import packages/modules
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb
import os
from pprint import pprint as pp
```

### LOAD THERMODB

```python
# ! ethanol
# thermodb file name
EtOH_thermodb_file = os.path.join(os.getcwd(), 'test', 'ethanol.pkl')
# load
EtOH_thermodb = ptdb.load_thermodb(EtOH_thermodb_file)
print(type(EtOH_thermodb))

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
```

### THERMODB LINK CONFIGURATION

```python
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

# check
# pp(thub1.check())
```

### RETRIEVE DATA

```python
# data
pp(datasource['CO2']['Pc']['value'])

# equation
pp(equationsource['CO2']['VaPr'].args)
pp(equationsource['CO2']['VaPr'].cal(T=298.15))
```

## FAQ

For any question, contact me on [LinkedIn](https://www.linkedin.com/in/sina-gilassi/) 


## Authors

- [@sinagilassi](https://www.github.com/sinagilassi)