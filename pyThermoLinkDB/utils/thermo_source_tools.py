# import libs
import logging
from typing import Dict, List, Optional, Tuple, TypeVar
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    CustomProperty,
)
from pythermodb_settings.utils import (
    find_component_by_id,
    set_component_id,
    measure_time,
)
# locals
from ..thermo import EquationSourceCore
from .unit_tools import UnitConversionFn

# NOTE: set logger
logger = logging.getLogger(__name__)

SourceValue = TypeVar("SourceValue")


def _component_ordered_data(
        data: Dict[str, SourceValue],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True
) -> Dict[str, Tuple[str, SourceValue]]:
    """
    Match source entries to requested components and return them keyed by output id.

    Input keys may use any component identifier supported by
    ``find_component_by_id``. Output keys always use ``component_key``. Entries
    that do not match any requested component are ignored.
    """
    matched_data: Dict[str, Tuple[str, SourceValue]] = {}

    for source_id, value in data.items():
        comp = find_component_by_id(
            id=source_id,
            components=components,
            case_sensitive=case_sensitive
        )

        if comp is None:
            continue

        output_id = set_component_id(comp, component_key)
        if output_id in matched_data:
            logger.warning(
                f"Multiple source entries matched component '{output_id}'. "
                f"Keeping the first entry and skipping '{source_id}'."
            )
            continue

        matched_data[output_id] = (source_id, value)

    return matched_data


# SECTION: map component property
@measure_time
def map_prop(
        data: Dict[str, CustomProperty],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True,
        output_unit: Optional[str] = None,
        unit_conversion_fn: Optional[UnitConversionFn] = None,
        **kwargs
) -> Optional[Tuple[Dict[str, float], List[float]]]:
    # NOTE: result initialization
    res_comp: Dict[str, float] = {}
    res_values: List[float] = []

    if not components:
        return res_comp, res_values

    if not data:
        logger.warning("Property source data is empty.")
        return None

    # NOTE: data keys can use any known component id format
    matched_data = _component_ordered_data(
        data=data,
        components=components,
        component_key=component_key,
        case_sensitive=case_sensitive
    )

    # NOTE: every requested component must be available in the source data
    missing_components = [
        set_component_id(comp, component_key)
        for comp in components
        if set_component_id(comp, component_key) not in matched_data
    ]
    if missing_components:
        logger.warning(
            f"Property source missing data for components: {missing_components}."
        )
        return None

    # NOTE: output order follows the provided components list
    for comp in components:
        output_id = set_component_id(comp, component_key)
        source_id, prop = matched_data[output_id]
        if prop.value is None:
            logger.warning(
                f"Property '{source_id}' has no value."
            )
            return None

        value = float(prop.value)
        if unit_conversion_fn is not None:
            if output_unit is None:
                logger.warning(
                    "Unit conversion function was provided but no target unit "
                    "was specified. Use 'output_unit'."
                )
                return None

            if prop.unit != output_unit:
                try:
                    value = unit_conversion_fn(
                        value=value,
                        from_unit=prop.unit,
                        to_unit=output_unit
                    )
                except Exception as e:
                    logger.error(
                        f"Error converting property '{source_id}' from "
                        f"'{prop.unit}' to '{output_unit}': {e}"
                    )
                    return None

        res_comp[output_id] = value
        res_values.append(value)

    return res_comp, res_values

# SECTION: map component equation source


def map_eq(
        data: Dict[str, EquationSourceCore],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True
) -> Optional[Tuple[Dict[str, EquationSourceCore], List[EquationSourceCore]]]:
    # NOTE: result initialization
    # ! id defined as component id or component reference
    res_comp: Dict[str, EquationSourceCore] = {}
    res_values: List[EquationSourceCore] = []

    if not components:
        return res_comp, res_values

    if not data:
        logger.warning("Equation source data is empty.")
        return None

    # NOTE: data keys can use any known component id format
    matched_data = _component_ordered_data(
        data=data,
        components=components,
        component_key=component_key,
        case_sensitive=case_sensitive
    )

    # NOTE: every requested component must be available in the source data
    missing_components = [
        set_component_id(comp, component_key)
        for comp in components
        if set_component_id(comp, component_key) not in matched_data
    ]
    if missing_components:
        logger.warning(
            f"Equation source missing data for components: {missing_components}."
        )
        return None

    # NOTE: output order follows the provided components list
    for comp in components:
        output_id = set_component_id(comp, component_key)
        _, eq = matched_data[output_id]
        res_comp[output_id] = eq
        res_values.append(eq)

    return res_comp, res_values
