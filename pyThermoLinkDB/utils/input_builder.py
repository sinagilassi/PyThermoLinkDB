# import libs
import logging
from typing import Optional, Dict, Any, Callable

# locals

# NOTE: Logger
logger = logging.getLogger(__name__)


# SECTION: Input Builder
def build_inputs(
        eq_inputs: Dict[str, Any],
        inputs: Dict[str, Any],
        unit_conversion_fn: Callable
):
    # NOTE: equation inputs configuration
    # ! units
    eq_input_units: Dict[str, str] = {
        k: v.get('unit', '') for k, v in eq_inputs.items()
    }
    eq_input_values: Dict[str, float] = {
        k: v.get('value', 0.0) for k, v in eq_inputs.items()
    }

    # NOTE: update input values with provided inputs, converting units if necessary
    # iterate through the expected inputs and convert if necessary
    for input_symbol, input_unit in eq_input_units.items():

        # >> check input value exists
        if input_symbol not in inputs.keys():
            continue  # skip if input value is not provided

        # set
        input_src = inputs[input_symbol]
        value_ = input_src['value']
        unit_ = input_src['unit']

        # >>> add to input values dict
        eq_input_values[input_symbol] = value_

        # ! convert input to expected unit if specified
        if (
            input_unit is not None and
            input_unit != unit_
        ):
            try:
                # convert to same unit for consistency
                converted_value = unit_conversion_fn.convert_from_to(
                    value=value_,
                    from_unit=unit_,
                    to_unit=input_unit
                )

                # >>> update input values dict with converted value
                eq_input_values[input_symbol] = converted_value
            except Exception as e:
                logger.error(
                    f"Error converting input '{input_symbol}' to required unit '{input_unit}': {e}")
                return None

    return eq_input_values
