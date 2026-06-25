# import libs
import logging
from typing import Protocol

# locals

# NOTE: Logger
logger = logging.getLogger(__name__)

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
