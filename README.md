# PyThermoLinkDB

![PyThermoLinkDB](https://drive.google.com/uc?export=view&id=1uwEMQLNJv7vIJ1Frq2cDORyhrqSwNRVS)

![Downloads](https://img.shields.io/pypi/dm/PyThermoLinkDB) ![PyPI](https://img.shields.io/pypi/v/PyThermoLinkDB) ![Python Version](https://img.shields.io/pypi/pyversions/PyThermoLinkDB.svg) ![License](https://img.shields.io/pypi/l/PyThermoLinkDB)

`PyThermoLinkDB` is a Python package providing a robust and efficient interface between `PyThermoDB` and other applications. It enables seamless thermodynamic data exchange, integration, and analysis. With PyThermoLinkDB, developers can easily link PyThermoDB to various tools, frameworks, and databases, streamlining thermodynamic workflows.

## ✨ **Key Features**

-   🔹 Simple and intuitive API
-   ⚡ Efficient data transfer and integration
-   📂 Compatible with multiple data formats
-   📚 Extensive documentation and examples

Ideal for researchers, engineers, and developers working with thermodynamic data, PyThermoLinkDB simplifies data integration and analysis, accelerating scientific discoveries and industrial applications.


## 🌐 **Google Colab**

You can run `PyThermoLinkDB` in Google Colab:

-  Basic Usage 1 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1JU1ljkHgKcBNe_CuSh2Bg7hoKwQUJti0?usp=sharing)


## 📥 **Installation**

Install `pyThermoLinkDB` and `PyThermoDB` with pip

```python
pip install pyThermoLinkDB
pip install PyThermoDB
```

## 🛠️ **Usage Example**

### 🔄 **Load ThermoDB**

This section demonstrates how to load thermodynamic data files from `PyThermoDB`.

Multiple thermodynamic databases are imported: one for CO2, one for methanol, and one for NRTL interaction parameters. Each database is loaded from a pickle file using the `load_thermodb` function, and then verified with the `check()` method to ensure data integrity.

```python
# import packages/modules
import os
from rich import print
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb

# SECTION CO2
CO2_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'carbon dioxide-1.pkl')
# load
CO2_thermodb = ptdb.load_thermodb(CO2_thermodb_file)
print(type(CO2_thermodb))

# check
print(CO2_thermodb.check())

# SECTION methanol
# thermodb file name
MeOH_thermodb_file = os.path.join(os.getcwd(), 'test', 'methanol-1.pkl')
print(f"thermodb file: {MeOH_thermodb_file}")
# load
MeOH_thermodb = ptdb.load_thermodb(MeOH_thermodb_file)
print(type(MeOH_thermodb))

MeOH_thermodb

# check
print(MeOH_thermodb.check())

# SECTION nrtl
# thermodb file name
nrtl_thermodb_file = os.path.join(
    os.getcwd(), 'test', 'thermodb_nrtl_1.pkl')
print(f"thermodb file: {nrtl_thermodb_file}")
# load
nrtl_thermodb = ptdb.load_thermodb(nrtl_thermodb_file)
print(type(nrtl_thermodb))

# check
print(nrtl_thermodb.check())
```

### 🔌 **Initialize Thermodb Hub**

This section demonstrates how to initialize a ThermoDB hub using the `init()` function, which creates a central repository for thermodynamic data.

The code shows adding different component databases (methanol, CO2) as well as interaction parameter data (NRTL) to the hub. The `items()` method is used to list all components currently stored in the hub.

```python
# init thermodb hub
thub1 = ptdblink.init()
print(type(thub1))

# add component thermodb
thub1.add_thermodb('MeOH', MeOH_thermodb)
thub1.add_thermodb('CO2', CO2_thermodb)
# matrix data
thub1.add_thermodb('NRTL', nrtl_thermodb)

# get components
print(thub1.items())
```

### ⚙️ **ThermoDB Link Configuration**

This section shows the format of the YAML configuration file used to define thermodynamic properties and equations for different compounds. Each component has a `DATA` section for properties (like critical pressure, temperature) and an `EQUATIONS` section for thermodynamic relationships. The configuration file structure helps maintain consistent property mapping across the database.

Thermodb rule format (`thermodb_config.yml`):

```yml
CO2:
  DATA:
    Pc: Pc
    Tc: Tc
    AcFa: AcFa
  EQUATIONS:
    vapor-pressure: VaPr
    heat-capacity: Cp_IG
acetylene:
  DATA:
    Pc: Pc
    Tc: Tc
    AcFa: AcFa
  EQUATIONS:
    vapor-pressure: VaPr
```

```python
# add thermodb rule
thermodb_config_file = os.path.join(os.getcwd(), 'test', 'thermodb_config.yml')

# all components
res_ = thub1.config_thermodb_rule(thermodb_config_file)
# selected components
#res_ = thub1.config_thermodb_rule(thermodb_config_file, names=["MeOH", "CO2"])
print(res_)
```

### 🔧 **Add/Update ThermoDB Rule**

This section demonstrates how to add or update a ThermoDB rule for a specific chemical compound (e.g., CO2). The rule includes critical data properties and equations related to the compound, which are then added to the ThermoDB using the `add_thermodb_rule` method.

```python
# update thermodb rule
thermodb_rule_CO2 = {
    'DATA': {
        'Pc': 'Pc1',
        'Tc': 'Tc1',
        'AcFa': 'AcFa1'
    },
    'EQUATIONS': {
        'vapor-pressure': 'VaPr1',
        'heat-capacity': 'Cp_IG1'
    }
}

# add thermodb rule for CO2
thub1.add_thermodb_rule('CO2', thermodb_rule_CO2)
```

### 🗑️ **Delete ThermoDB Rule**

This section demonstrates how to delete a specific ThermoDB rule using the `delete_thermodb_rule` method. In this example, the rule associated with 'CO2' is being removed.

```python
# delete thermodb rule for CO2
thub1.delete_thermodb_rule('CO2')
```

### 🔨 **Build ThermoDB Hub**

This section demonstrates the process of building data sources and equation sources using the `build` method, and then prints the resulting objects. Additionally, it showcases accessing and printing the `hub` attribute.

```python
# build
datasource, equationsource = thub1.build()
print(datasource)
print(equationsource)

# hub
print(thub1.hub)
```

### 📊 **Retrieve Data/Equation**

This section demonstrates how to access various thermodynamic data and equations from the built ThermoDB hub. Examples include retrieving critical properties (Pc, Tc) for different components, NRTL interaction parameters, and calculating values using vapor pressure and activity coefficient equations at specified conditions.

```python
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
eq1_ = equationsource['CO2']['VaPr']
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
```

## ❓ **FAQ**

For any question, contact me on [LinkedIn](https://www.linkedin.com/in/sina-gilassi/)


## 👨‍💻 **Authors**

- [@sinagilassi](https://www.github.com/sinagilassi)