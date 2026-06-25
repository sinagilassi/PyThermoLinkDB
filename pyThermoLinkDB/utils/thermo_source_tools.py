# import libs
import logging
from typing import Any, Dict, List, Optional, Tuple
from pythermodb_settings.models import Component, ComponentKey, CustomProperty, CustomConstant
from pythermodb_settings.utils import generate_component_references, find_component_by_id, find_components_by_ids
# locals

# NOTE: set logger
logger = logging.getLogger(__name__)


# SECTION:
def data_transformer(
        data: Dict[str, CustomProperty],
        components: Optional[List[Component]],
        component_key: Optional[ComponentKey] = None,
        case_sensitive: bool = True
) -> Tuple[Dict[str, float], List[float]]:
    # NOTE: result initialization
    res_comp: Dict[str, float] = {}
    res_values: List[float] = []

    # NOTE: component ids
    component_ids: List[str] = list(data.keys())

    # ! find components by ids
    if components is not None:
        components_ = find_components_by_ids(
            ids=component_ids,
            components=components,
            case_sensitive=case_sensitive
        )

        # >> check
        if not components_:
            logger.warning(
                f"No components found for ids: {component_ids}. "
                f"Returning empty results."
            )
            return res_comp, res_values

    # NOTE: no components means no transformation is needed
    if not components:
        # iterate over the data and extract values
        for symbol, prop in data.items():
            if prop.value is not None:
                res_comp[symbol] = prop.value
                res_values.append(prop.value)
            else:
                logger.warning(
                    f"Property '{symbol}' has no value and will be skipped.")

    # NOTE: components are provided, so we need to transform the data
    else:

    return res_comp, res_values
