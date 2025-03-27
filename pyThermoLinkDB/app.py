# import packages/modules

# local
from .config import __version__, __author__, __description__
from .docs import ThermoDBHub


def init() -> ThermoDBHub:
    '''
    Init thermolinkdb app

    Parameters
    ----------
    None

    Returns
    -------
    ThermoDBHub
        ThermoDBHub object
    '''
    try:
        # init thermolink
        return ThermoDBHub()
    except Exception as e:
        raise Exception("Error: {}".format(e))
