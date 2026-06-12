# import libs
import logging
from typing import Dict, Literal, Any, Optional, List
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from ..models.component_models import PropResult

# NOTE: Logger
logger = logging.getLogger(__name__)


class ConstantsSourceCore:
    pass
