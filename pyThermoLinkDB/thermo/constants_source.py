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

    def __init__(
            self,
            source: Source,
    ) -> None:
        """
        Initialize ConstantsSourceCore with a source.

        Parameters
        ----------
        source : Source
            The source containing data for calculations.
        """
        # NOTE: source
        self.source = source
