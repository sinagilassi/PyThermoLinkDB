# import packages/modules
import os
# local
from .config import __version__, __author__, __description__
from .docs import ThermoDBHub, ThermoLink


def get_version() -> str:
    '''
    Get the current version
    '''
    return __version__


def get_author() -> str:
    '''
    Get the author
    '''
    return __author__


def des() -> str:
    '''
    Get the description
    '''
    return __description__


def init() -> ThermoDBHub:
    '''
    Init thermolink

    Parameters
    ----------
    None

    Returns
    -------
    ThermoDBHub : ThermoDBHub
        A thermolink object
    '''
    try:
        # init thermolink
        ThermoDBHubC = ThermoDBHub()
        return ThermoDBHubC
    except Exception as e:
        raise Exception("Error: {}".format(e))


if __name__ == "__main__":
    print(get_version())
