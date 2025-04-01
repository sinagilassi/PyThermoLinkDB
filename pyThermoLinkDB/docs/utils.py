# import libs
import pandas as pd
from typing import Dict, List, Tuple
# locals


def generate_summary(hub: Dict):
    '''
    Generate summary table of the thermodynamic database hub.
    
    Parameters
    ----------
    hub : dict
        The thermodynamic database hub.
    '''
    try:
        pass
    except Exception as e:
        raise Exception(f"Error in generating summary: {e}") from e