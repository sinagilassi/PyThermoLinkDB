# import packages/modules
from rich import print
import pycuc
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import (
    mkeqss,
    EquationSourceCore,
    EquationSourcesCore,
)
from pyThermoLinkDB.utils.input_builder import validate_and_build_inputs
from pythermodb_settings.utils import set_component_id

# ! model source & components
from examples.model_source_1 import model_source, CO2, C2H5OH


# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# MODEL SOURCE
# =======================================
datasource = model_source.data_source
equationsource = model_source.equation_source

# =======================================
# TEST
# =======================================
# NOTE: by formula-state
# data
dt1_ = datasource['CO2-g']['EnFo_IG']
print(type(dt1_))
print(dt1_)

# equation
eq1_ = equationsource['CO2-g']['Cp_IG']
print(type(eq1_))
print(eq1_)
print(eq1_.args)
print(eq1_.cal(T=298.15))

# =======================================
# UNIT CONVERSION SETTINGS
# =======================================
# NOTE: create unit conversion function using pycuc
unit_conversion_fn = pycuc.convert_from_to

# NOTE: create unit availability function using pycuc
unit_availability_fn = pycuc.is_unit_available

# =======================================
# INPUTS
# =======================================
# NOTE: universal inputs
runtime_inputs = {
    "T": {"value": 25.0, "unit": "C"},
    "P": {"value": 101325.0, "unit": "Pa"},
    "Tc": {"value": 302.0, "unit": "K"},
}

runtime_inputs_symbols = list(runtime_inputs.keys())

# =======================================
# MAKE EQUATION SOURCES DIRECTLY
# =======================================
components = [CO2, C2H5OH]
component_key = 'Name-State'

# build list (optional)
build_list = ["Cp_IG", "Cp_LIQ", "EnFo_IG"]

# SECTION: Build equations
equation_sources: dict[str, EquationSourcesCore] | None = mkeqss(
    components=components,
    model_source=model_source,
    component_key=component_key,
    build_all=True,
    build_list=build_list,  # ! optional
    build_check=True,  # ! optional
)

# print the equation source objects
print(equation_sources)

# >> check
if equation_sources is None:
    raise ValueError("No equation sources found.")

# =======================================
# DICTIONARY KEYS
# =======================================
component_ids = [
    set_component_id(component, component_key)
    for component in components
]
print(component_ids)
print(equation_sources.keys())

# =======================================
# ACCESS ETHANOL EQUATION SOURCES
# =======================================
ethanol_id = set_component_id(C2H5OH, component_key)
ethanol_eqs = equation_sources[ethanol_id]

# ! all available equations
print(ethanol_eqs.all_available_equations())

# ! check availability of specific equations
print(ethanol_eqs.check_availability(names=['Cp_IG', 'Cp_LIQ']))
print(ethanol_eqs.check_availability(names=['Cp_IG', 'Unknown_Prop']))

# ! all available equation symbols
print(ethanol_eqs.all_available(names=['Cp_IG', 'Cp_LIQ']))
print(ethanol_eqs.all_available(
    names=['Cp_IG', 'Cp_LIQ', 'Unknown_Prop'])
)

# ! source all equations for the component
print(ethanol_eqs.src)

# ! inputs sources for all equations
print(ethanol_eqs.inputs_src)

# ! input symbols sources for all equations
print(ethanol_eqs.inputs_symbols_src)

# ! validate all inputs availability and units for all equations
validation_results = ethanol_eqs.validate_all_inputs(
    inputs=runtime_inputs_symbols,
    unit_availability_fn=unit_availability_fn
)
print(validation_results)

# ? select Cp_IG equation source
Cp_IG_eq: EquationSourceCore | None = ethanol_eqs.select(name='Cp_IG')
print(Cp_IG_eq)
if Cp_IG_eq is not None:
    # inputs
    print(Cp_IG_eq.inputs)

    # ! validate and build inputs
    input_args = validate_and_build_inputs(
        Cp_IG_eq.inputs,
        runtime_inputs,
        unit_conversion_fn=unit_conversion_fn,
        unit_availability_fn=unit_availability_fn
    )
    # >> log
    print(input_args)

    # calc
    print(Cp_IG_eq.calc(**input_args))

# ? select Cp_LIQ equation source
Cp_LIQ_eq: EquationSourceCore | None = ethanol_eqs.select(name='Cp_LIQ')
print(Cp_LIQ_eq)
if Cp_LIQ_eq is not None:
    # inputs
    print(Cp_LIQ_eq.args)
    print(Cp_LIQ_eq.inputs)
    print(Cp_LIQ_eq.arg_mappings)

    # ! validate and build inputs
    input_args = validate_and_build_inputs(
        Cp_LIQ_eq.inputs,
        runtime_inputs,
        unit_conversion_fn=unit_conversion_fn,
        unit_availability_fn=unit_availability_fn
    )
    # >> log
    print(input_args)

    # calc
    print(Cp_LIQ_eq.calc(**input_args))

# >> unknown equation
unknown_eq: EquationSourceCore | None = ethanol_eqs.select(
    name='Unknown_Prop'
)
print(unknown_eq)

# =======================================
# ACCESS CO2 EQUATION SOURCES
# =======================================
CO2_id = set_component_id(CO2, component_key)
CO2_eqs = equation_sources[CO2_id]

print(CO2_eqs.all_available_equations())
print(CO2_eqs.check_availability(names=['Cp_IG', 'Cp_LIQ']))
