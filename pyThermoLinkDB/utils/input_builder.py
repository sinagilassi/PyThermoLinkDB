# import libs
import logging
from typing import Dict, Any, Protocol, Tuple

# locals

# NOTE: Logger
logger = logging.getLogger(__name__)

# SECTION: Check unit availability
# NOTE: Protocol for unit availability function used by check_unit_availability


class UnitAvailabilityFn(Protocol):
    """
    Callable unit availability interface used by ``check_unit_availability``.

    The callable must accept a unit label and return a boolean indicating
    whether the unit is recognized and supported for conversion. This allows
    the input builder to verify that all required units are available before
    attempting conversions.
    """

    def __call__(self, unit: str) -> bool:
        ...

# NOTE: check_unit_availability function


def check_unit_availability(
        eq_inputs: Dict[str, Any],
        unit_availability_fn: UnitAvailabilityFn
) -> Tuple[bool, Dict[str, bool]]:
    """
    Check that all units required by equation inputs are available.

    Parameters
    ----------
    eq_inputs : Dict[str, Any]
        Expected equation inputs keyed by input symbol. Each entry may define an
        expected ``unit``.
    unit_availability_fn : UnitAvailabilityFn
        Function used to check if a unit is recognized and supported for
        conversion. For example, a function that checks against a list of valid
        units or queries a unit conversion library.

    Returns
    -------
    bool, Dict[str, bool]
        A tuple where the first element is a boolean indicating if all required

    Notes
    -----
    This function can be used as a preliminary check before attempting to build
    inputs, allowing the caller to catch missing units early and avoid conversion
    errors later on.
    """
    try:
        # detailed of unit availability check
        res = {}

        # looping through the expected inputs and check unit availability
        for input_symbol, input_config in eq_inputs.items():
            unit = input_config.get('unit')
            if unit and not unit_availability_fn(unit):
                logger.error(
                    f"Required unit '{unit}' for input '{input_symbol}' is not available."
                )
                res[input_symbol] = False
            else:
                res[input_symbol] = True

        # check all units availability
        all_available = all(res.values())

        return all_available, res
    except Exception as e:
        logger.error(f"Error checking unit availability: {e}")
        return False, {}

# SECTION: Input Builder
# NOTE: check all eq_inputs are available in inputs


def check_inputs_availability(
        eq_inputs: Dict[str, Any],
        inputs: Dict[str, Any]
) -> Tuple[bool, Dict[str, bool]]:
    """
    Check that all expected equation inputs are provided in the runtime inputs.

    Parameters
    ----------
    eq_inputs : Dict[str, Any]
        Expected equation inputs keyed by input symbol.
    inputs : Dict[str, Any]
        Runtime input values keyed by input symbol.

    Returns

    bool, Dict[str, bool]
        A tuple where the first element is a boolean indicating if all expected inputs are provided, and the second element is a dictionary detailing the availability of each input.
    """
    try:
        # detailed of unit availability check
        res = {}

        # looping through the expected inputs and check availability
        for input_symbol in eq_inputs.keys():
            if input_symbol not in inputs.keys():
                logger.warning(
                    f"Expected input '{input_symbol}' is not provided in runtime inputs."
                )
                res[input_symbol] = False
            else:
                res[input_symbol] = True

        # check all inputs availability
        all_available = all(res.values())

        # res
        return all_available, res
    except Exception as e:
        logger.error(f"Error checking inputs availability: {e}")
        return False, {}

# NOTE: Protocol for unit conversion function used by build_inputs


class UnitConversionFn(Protocol):
    """
    Callable unit conversion interface used by ``build_inputs``.

    The callable must accept a numeric value, a source unit, and a target unit,
    then return the value converted to the target unit. Callers must ensure the
    provided conversion function supports every unit pair that may appear in the
    equation input definitions and runtime inputs.
    """

    def __call__(
        self,
        *,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        ...

# NOTE: build_inputs function


def build_inputs(
        eq_inputs: Dict[str, Any],
        inputs: Dict[str, Any],
        unit_conversion_fn: UnitConversionFn
) -> Dict[str, float] | None:
    """
    Build equation input values from defaults and provided runtime inputs.

    Parameters
    ----------
    eq_inputs : Dict[str, Any]
        Expected equation inputs keyed by input symbol. Each entry may define a
        default ``value`` and expected ``unit``.
    inputs : Dict[str, Any]
        Runtime input values keyed by input symbol. Each entry should define a
        ``value`` and ``unit``.
    unit_conversion_fn : UnitConversionFn
        Function used to convert runtime input values to the units required by
        ``eq_inputs``. For example, ``pycuc.convert_from_to`` may be passed
        directly.

    Returns
    -------
    Dict[str, float] | None
        Input values in the units required by ``eq_inputs``. Returns ``None`` if
        a required unit conversion fails.

    Notes
    -----
    This function assumes unit labels are valid and compatible with the provided
    conversion function. Make sure the converter can handle every unit pair that
    may be requested; otherwise conversion errors are logged and ``None`` is
    returned.
    """
    try:
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
                logger.warning(
                    f"Input '{input_symbol}' not provided in runtime inputs; using default value {eq_input_values[input_symbol]} {input_unit}"
                )
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
                    converted_value = unit_conversion_fn(
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
    except Exception as e:
        logger.error(f"Error building inputs: {e}")
        return None
