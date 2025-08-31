# import libs
import logging
from typing import Dict, Any
# local
from .convertor import Convertor

# NOTE: logger
logger = logging.getLogger(__name__)


def create_rules_from_str(data: str) -> Dict[str, Any]:
    '''
    Create rules from a string (YAML, JSON, or Markdown)

    Parameters
    ----------
    data: str
        File path to the rules file (YAML, JSON, or Markdown)

    Returns
    -------
    Dict
        Rules dictionary
    '''
    try:
        # SECTION: create convertor
        convertor = Convertor()

        # SECTION: determine format
        data_format = convertor.which_format(data)

        # normalized format
        normalized_format = data_format.lower()

        # check
        if normalized_format == "markdown":
            # ! markdown
            # For markdown, we can return a simple dict with the raw data
            return {}
        elif normalized_format in ["yaml", "json"]:
            # ! yaml or json
            return convertor.str_to_dict(
                data=data,
                format=normalized_format
            )
        else:
            logging.error(f"Unsupported format: {format}")
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        logger.error(f"Error in create_rules_from_str: {e}")
        raise Exception(f"Error in create_rules_from_str: {e}")
