# import libs
import logging
import pycuc
from typing import Dict, Any
# local
from pyThermoLinkDB.utils.input_builder import (
    check_inputs_availability,
    check_unit_availability,
    UnitAvailabilityFn,
    build_inputs,
    UnitConversionFn
)

# NOTE: logger
logger = logging.getLogger(__name__)

# SECTION: unit availability check
# NOTE: create unit availability function using pycuc
unit_availability_fn = pycuc.is_unit_available

# NOTE: create equation input definitions
eq_inputs = {
    "T": {"value": 0, "unit": "K"},
    "P": {"value": 0, "unit": "bar"},
    "V": {"value": 0, "unit": "m^3"},
}

# NOTE: check unit availability
all_available, availability_details = check_unit_availability(
    eq_inputs,
    unit_availability_fn
)
# >> log
print(all_available)
print(availability_details)


# SECTION: input builder
# NOTE: create unit conversion function using pycuc
unit_conversion_fn = pycuc.convert_from_to

# NOTE: create equation input definitions
eq_inputs = {
    "T": {"value": 0, "unit": "K"},
    "P": {"value": 0, "unit": "bar"},
    "V": {"value": 0, "unit": "L"},
    "Q": {"value": 0, "unit": "kJ"},
}

# NOTE: create runtime inputs
inputs = {
    "T": {"value": 25.0, "unit": "C"},
    "P": {"value": 101325.0, "unit": "Pa"},
    "V": {"value": 0.001, "unit": "m3"},
}

# NOTE: check inputs availability
inputs_available, inputs_availability_details = check_inputs_availability(
    eq_inputs,
    inputs
)
# >> log
print(inputs_available)
print(inputs_availability_details)

# NOTE: build inputs
built_inputs = build_inputs(eq_inputs, inputs, unit_conversion_fn)
# >> log
print(built_inputs)
