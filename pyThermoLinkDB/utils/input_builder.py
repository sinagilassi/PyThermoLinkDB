# import libs
import logging
from typing import Dict, Any, Protocol, Tuple, List
from pythermodb_settings.utils import measure_time

# locals

# NOTE: Logger
logger = logging.getLogger(__name__)


# SECTION: Utils
def _extract_input_symbols(inputs: Dict[str, Any]) -> List[str]:
    """
    Extract input symbols from runtime inputs.

    Parameters
    ----------
    inputs : Dict[str, Any]
        Runtime input values keyed by input symbol. Each entry should define a
        ``value`` and ``unit``.

    Returns
    -------
    List[str]
        A list of input symbols extracted from the runtime inputs.

    Notes
    -----
    This function assumes that each entry in the `inputs` dictionary contains a valid `symbol` key. If any entry is missing the `symbol` key or if the value is not a string, an error will be logged and an empty list will be returned.
    """
    try:
        symbols = []
        for input_key, input_value in inputs.items():
            symbol = input_value.get('symbol')
            if isinstance(symbol, str):
                symbols.append(symbol)
            else:
                logger.error(
                    f"Input '{input_key}' is missing a valid 'symbol' key or it is not a string."
                )
                return []
        return symbols
    except Exception as e:
        logger.error(f"Error extracting input symbols: {e}")
        return []

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
        inputs: List[str]
) -> Tuple[bool, Dict[str, bool]]:
    """
    Check that all expected equation inputs are provided in the runtime inputs.

    Parameters
    ----------
    eq_inputs : Dict[str, Any]
        Expected equation inputs keyed by input symbol.
    inputs : List[str]
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
            if input_symbol not in inputs:
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

# SECTION: check all eq_inputs are available in inputs and check required units are available before building inputs


def validate_inputs_availability_and_units(
        eq_inputs: Dict[str, Any],
        inputs: Dict[str, Any],
        unit_availability_fn: UnitAvailabilityFn,
) -> Tuple[bool, Dict[str, bool], bool, Dict[str, bool]]:
    """
    Validate that all expected equation inputs are provided in the runtime inputs and that all required units are available.

    Parameters
    ----------
    eq_inputs : Dict[str, Any]
        Expected equation inputs keyed by input symbol. Each entry may define an expected ``unit``.
    inputs : Dict[str, Any]
        Runtime input values keyed by input symbol. Each entry should define a ``value`` and ``unit``.
    unit_availability_fn : UnitAvailabilityFn
        Function used to check if a unit is recognized and supported for conversion.

    Returns
    -------
    Tuple[bool, Dict[str, bool], bool, Dict[str, bool]]
        A tuple containing:
            - A boolean indicating if all expected inputs are provided.
            - A dictionary detailing the availability of each expected input.
            - A boolean indicating if all required units are available.
            - A dictionary detailing the availability of each required unit.
    """
    try:
        # input symbols
        inputs_symbols = _extract_input_symbols(inputs)

        # check inputs availability
        inputs_available, inputs_availability_details = check_inputs_availability(
            eq_inputs,
            inputs_symbols
        )

        # check unit availability
        units_available, units_availability_details = check_unit_availability(
            eq_inputs,
            unit_availability_fn
        )

        return inputs_available, inputs_availability_details, units_available, units_availability_details
    except Exception as e:
        logger.error(f"Error validating inputs and units availability: {e}")
        return False, {}, False, {}

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

# SECTION: Build & check inputs


@measure_time
def validate_and_build_inputs(
        eq_inputs: Dict[str, Any],
        inputs: Dict[str, Any],
        unit_conversion_fn: UnitConversionFn,
        unit_availability_fn: UnitAvailabilityFn,
        **kwargs
) -> Dict[str, float]:
    """
    Validate equation inputs and build runtime input values.

    All expected equation inputs must be present in the runtime inputs. This
    makes the returned dictionary suitable for direct use as calculation
    arguments and avoids silently falling back to default values.

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
    unit_availability_fn : UnitAvailabilityFn
        Function used to check if a unit is recognized and supported for
        conversion. Expected equation input units are checked before building
        inputs.
    **kwargs : Dict[str, Any]
        Additional keyword arguments for future extensibility.
            - mode : Literal['silent', 'log', 'attach'], optional
                Mode for time measurement logging. Default is 'silent'.

    Returns
    -------
    Dict[str, float] | None
        Input values in the units required by ``eq_inputs``. Returns ``None`` if
        a required unit conversion fails or if required inputs are missing.
    """
    try:
        # NOTE: check required target units before building args
        units_available, _ = check_unit_availability(
            eq_inputs,
            unit_availability_fn
        )
        if not units_available:
            logger.error(
                "One or more required units for equation inputs are not available."
            )
            raise ValueError(
                "Missing required units for equation input building.")

        # NOTE: inputs symbols
        inputs_symbols = _extract_input_symbols(inputs)

        # NOTE: all expected inputs must be provided before building args
        inputs_available, _ = check_inputs_availability(
            eq_inputs,
            inputs_symbols
        )
        if not inputs_available:
            logger.error(
                "One or more expected inputs for the equation are not provided in runtime inputs."
            )
            raise ValueError(
                "Missing required inputs for equation calculation.")

        # NOTE: build inputs
        res_ = build_inputs(
            eq_inputs=eq_inputs,
            inputs=inputs,
            unit_conversion_fn=unit_conversion_fn
        )

        # check build result
        if res_ is None:
            logger.error(
                "Failed to build inputs due to unit conversion error."
            )
            raise ValueError("Input building failed.")

        return res_
    except Exception as e:
        logger.error(f"Error validating and building inputs: {e}")
        raise
