# import libs
from typing import List, Tuple, Literal


# SECTION: configure mixture name by ordered component names (alphabetical)
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
