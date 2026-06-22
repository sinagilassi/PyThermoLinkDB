# import packages/modules
from typing import Dict
import os
from rich import print
import pycuc
import pyThermoLinkDB as ptdblink
from pyThermoLinkDB import load_and_build_model_source
from pyThermoLinkDB.models import ModelSource
import pyThermoDB as ptdb
from pythermodb_settings.models import (
    Component,
    ComponentRule,
    ComponentThermoDBSource,
)
# ! pyThermoLinkDB
from pyThermoLinkDB import (
    mkdt,
    mkeq,
    mkeqs,
    EquationSourceCore,
    DataSourceCore,
    EquationSourcesCore
)
from pyThermoLinkDB.utils.input_builder import (
    check_inputs_availability,
    check_unit_availability,
    UnitAvailabilityFn,
    build_inputs,
    UnitConversionFn,
    validate_and_build_inputs,
    validate_inputs_availability_and_units
)
# ! model source & components
from examples.model_source_1 import model_source, CO2, C2H5OH


# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# 🌍 LOAD THERMODB
# =======================================
# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current dir: {current_dir}")

# =======================================
# 🏗️ LOAD & BUILD
# =======================================

# get data source and equation source
datasource = model_source.data_source
equationsource = model_source.equation_source

# =======================================
# ✅ unit conversion settings
# =======================================
# NOTE: create unit conversion function using pycuc
unit_conversion_fn = pycuc.convert_from_to

# NOTE: create unit availability function using pycuc
unit_availability_fn = pycuc.is_unit_available

# =======================================
# ✅ inputs
# =======================================
# NOTE: universal inputs
runtime_inputs = {
    "T": {"value": 25.0, "unit": "C"},
    "P": {"value": 101325.0, "unit": "Pa"},
    "Tc": {"value": 302.0, "unit": "K"},
}

runtime_inputs_symbols = list(runtime_inputs.keys())

# =======================================
# ✅ make equation source for ethanol
# =======================================
# SECTION: Build equations
# ! make equation source
ethanol_eqs: EquationSourcesCore | None = mkeqs(
    component=C2H5OH,
    model_source=model_source,
    component_key='Name-State',
    build_all=True,  # build all equations for the component
    # optional list of specific equations to build, if None or empty, all equations will be built
    build_list=["Cp_IG", "Cp_LIQ"]
)
# print the equation source object
print(ethanol_eqs)

# NOTE: >> check ethane equations
if ethanol_eqs is None:
    raise ValueError("No equation source found for ethanol.")

# NOTE: >> check build status
print(ethanol_eqs.summary())
print(ethanol_eqs.build_status())

# NOTE: results
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
Cp_IG_eq_: EquationSourceCore | None = ethanol_eqs.select(name='Cp_IG')
print(Cp_IG_eq_)
if Cp_IG_eq_ is not None:
    # inputs
    print(Cp_IG_eq_.inputs)

    # ! check inputs availability
    # inputs_available, inputs_availability_details = check_inputs_availability(
    #     Cp_IG_eq_.inputs,
    #     inputs
    # )

    # ! build inputs
    # input_args = build_inputs(
    #     Cp_IG_eq_.inputs,
    #     inputs,
    #     unit_conversion_fn=unit_conversion_fn
    # )
    # >> log
    # print(input_args)

    # ! validate and build inputs
    input_args = validate_and_build_inputs(
        Cp_IG_eq_.inputs,
        runtime_inputs,
        unit_conversion_fn=unit_conversion_fn,
        unit_availability_fn=unit_availability_fn
    )
    # >> log
    print(input_args)

    # calc
    print(Cp_IG_eq_.calc(**input_args))

# ? make Cp_LIQ equation source
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
