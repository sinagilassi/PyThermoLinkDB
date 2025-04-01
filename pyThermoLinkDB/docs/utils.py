# import libs
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
        # NOTE: sub items
        items = {}
        
        for key, value in hub.items():
            # check 
            if value:
                items[key] = list(value.keys())
                
        # NOTE: return summary
        return items
    except Exception as e:
        raise Exception(f"Error in generating summary: {e}") from e