# import libs
from pythermodb_settings.models import Component


# NOTE: create component
# ! propane
# carbon dioxide
CO2 = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g',
)

# Hydrogen
H2 = Component(
    name='hydrogen',
    formula='H2',
    state='g',
)

# methanol
CH3OH = Component(
    name='methanol',
    formula='CH3OH',
    state='l',
)

# ethanol
C2H5OH = Component(
    name='ethanol',
    formula='C2H5OH',
    state='l',
)

# water
H2O = Component(
    name='water',
    formula='H2O',
    state='g',
)

# Carbon monoxide
CO = Component(
    name='carbon monoxide',
    formula='CO',
    state='g',
)

# ethylene
C2H4 = Component(
    name='ethylene',
    formula='C2H4',
    state='g',
)

# ethane
C2H6 = Component(
    name='ethane',
    formula='C2H6',
    state='g',
)

# CH4
CH4 = Component(
    name='methane',
    formula='CH4',
    state='g',
)

# ! components
components = [C2H4, C2H6, CO2, C2H5OH, CH3OH, CH4]
