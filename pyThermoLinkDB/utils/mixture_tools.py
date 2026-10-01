# import libs
import logging
from typing import List, Tuple, Literal, Dict, Any

# NOTE: logger setup
logger = logging.getLogger(__name__)


# ! ::: configure mixture name by ordered component names (alphabetical)
def canonicalize_mixture_name(
        mixture_name: str,
        delimiter: str = "|",
        case: Literal['lower', 'upper'] | None = None
) -> Tuple[str, List[str]]:
    """
    Configure mixture name by sorting component names alphabetically.

    Parameters
    ----------
    mixture_name : str
        Mixture name with component names separated by a delimiter.
    delimiter : str, optional
        Delimiter used to separate component names in the mixture name,
        by default "|".
    case : Literal['lower', 'upper'] | None, optional
        Case conversion for the output mixture name. If 'lower', all
        component names are converted to lowercase. If 'upper', all
        component names are converted to uppercase. If None, no case
        conversion is applied, by default None.

    Returns
    -------
    Tuple[str, List[str]]
        A tuple containing:
        - The configured mixture name with component names sorted alphabetically.
        - A list of the individual component names in the order they appear
        in the sorted mixture name.
    """
    components = [
        component.strip() for component in mixture_name.split(delimiter)
    ]

    if case == "lower":
        components = [component.lower() for component in components]
    elif case == "upper":
        components = [component.upper() for component in components]

    components = sorted(components)

    return delimiter.join(components), components

# ! ::: Sort Mixture Ids


def sort_mixture_id(
        mixture_id: str,
        delimiter: str = '|',
) -> str:
    """
    Sort the given list of mixture ID.

    Parameters
    ----------
    mixture_id: str
        The mixture ID to sort.
    delimiter: str, optional
        The delimiter used to split the mixture ID, by default '|'

    Returns
    -------
    str
        The sorted mixture ID.
    """
    elements = mixture_id.split(delimiter)
    elements.sort()
    return delimiter.join(elements)

# ! ::: Check Mixture Id Exists


def normalize_mixture_data(
        data: Dict[str, Any],
        delimiter: str = '|'
) -> Dict[str, Any]:
    """
    Extract mixture IDs from the given data dictionary.

    Parameters
    ----------
    data : Dict[str, Any]
        The data dictionary to check for mixture IDs.
    delimiter : str, optional
        The delimiter used to identify mixture IDs, by default '|'

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the normalized mixture IDs as keys and their corresponding values from the input data dictionary.
    """
    return {
        sort_mixture_id(
            mixture_id=key,
            delimiter=delimiter
        ): value for key, value in data.items() if delimiter in key
    }
