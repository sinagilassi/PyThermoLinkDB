# PyThermoDBLink

![PyThermoLinkDB](./statics/header-1.png)

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

```python
# add thermodb rule
thermodb_config_file = os.path.join(os.getcwd(), 'test', 'thermodb_config.yml')

# all components
res_ = thub1.config_thermodb_rule(thermodb_config_file)
# selected components
#res_ = thub1.config_thermodb_rule(thermodb_config_file, names=["MeOH", "CO2"])
print(res_)
```

### 🔨 **Build ThermoDB Hub**

```python
# build
datasource, equationsource = thub1.build()
print(datasource)
print(equationsource)

# hub
print(thub1.hub)
```

### 📊 **Retrieve Data**

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