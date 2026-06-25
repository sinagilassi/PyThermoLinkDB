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
    Match source entries to requested components.

    Parameters
    ----------
    data : Dict[str, SourceValue]
        Source records keyed by component identifier. The key may use any
        identifier format recognized by ``find_component_by_id``.
    components : List[Component]
        Components requested by the caller. Only records matching these
        components are retained.
    component_key : ComponentKey
        Identifier format used for output keys.
    case_sensitive : bool, optional
        Whether source key matching should be case-sensitive, by default True.

    Returns
    -------
    Dict[str, Tuple[str, SourceValue]]
        Mapping keyed by output component id. Each value is a tuple containing
        the original source id and the matched source value.

    Notes
    -----
    Extra records in ``data`` that do not match a requested component are
    ignored. If multiple records match the same requested component, the first
    record is retained and later duplicates are skipped with a warning.
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
    """
    Map component property sources into component order.

    Parameters
    ----------
    data : Dict[str, CustomProperty]
        Property records keyed by component identifier. Keys may use any
        component id format recognized by ``find_component_by_id``.
    components : List[Component]
        Components to extract, in the desired output order.
    component_key : ComponentKey
        Identifier format used for output dictionary keys.
    case_sensitive : bool, optional
        Whether source key matching should be case-sensitive, by default True.
    output_unit : Optional[str], optional
        Target unit for all returned values. Required when
        ``unit_conversion_fn`` is provided.
    unit_conversion_fn : Optional[UnitConversionFn], optional
        Conversion function called as
        ``unit_conversion_fn(value=value, from_unit=prop.unit, to_unit=output_unit)``.
        If omitted, values are returned in their source units.
    **kwargs
        Reserved for compatibility with timed-call wrappers and future options.
            - mode : Literal['silent', 'log', 'attach'], optional
                Mode for time measurement logging. Default is 'silent'.

    Returns
    -------
    Optional[Tuple[Dict[str, float], List[float]]]
        A tuple containing:
        - component-keyed values using ``component_key``;
        - values ordered exactly like ``components``.
        Returns ``None`` if source data is empty, any requested component is
        missing, a property value is missing, or unit conversion cannot be
        performed.

    Notes
    -----
    Extra records in ``data`` are ignored. All requested components must be
    available in ``data``; otherwise no partial result is returned.
    """
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


@measure_time
def map_eq(
        data: Dict[str, EquationSourceCore],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True,
        **kwargs
) -> Optional[Tuple[Dict[str, EquationSourceCore], List[EquationSourceCore]]]:
    """
    Map component equation sources into component order.

    Parameters
    ----------
    data : Dict[str, EquationSourceCore]
        Equation sources keyed by component identifier. Keys may use any
        component id format recognized by ``find_component_by_id``.
    components : List[Component]
        Components to extract, in the desired output order.
    component_key : ComponentKey
        Identifier format used for output dictionary keys.
    case_sensitive : bool, optional
        Whether source key matching should be case-sensitive, by default True.
    **kwargs : Dict[str, Any]
        Additional keyword arguments for future extensibility.
            - mode : Literal['silent', 'log', 'attach'], optional
                Mode for time measurement logging. Default is 'silent'.

    Returns
    -------
    Optional[Tuple[Dict[str, EquationSourceCore], List[EquationSourceCore]]]
        A tuple containing:
        - component-keyed equation sources using ``component_key``;
        - equation sources ordered exactly like ``components``.
        Returns ``None`` if source data is empty or any requested component is
        missing.

    Notes
    -----
    Extra records in ``data`` are ignored. All requested components must be
    available in ``data``; otherwise no partial result is returned.
    """
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
