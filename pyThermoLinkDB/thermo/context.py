# import libs
import logging
from typing import Optional, Dict, Any
from pythermodb_settings.models import CustomProperty, Component, ComponentKey
from pythermodb_settings.utils import set_component_id
# locals
from ..models.source import ModelSource
from .source import Source

# NOTE: logger setup
logger = logging.getLogger(__name__)


class Context:
    """
    Context class for managing model sources, data sources, equation sources, and pools of constants/variables.
    """

    # NOTE: attributes
    _pools: Dict[str, CustomProperty] = {}

    # ! required keys
    _required_keys = {'symbol', 'value', 'unit'}

    def __init__(
            self,
            model_source: ModelSource,
            component_key: ComponentKey
    ):
        """
        Context class for managing model sources, data sources, equation sources, and pools of constants/variables.

        Parameters
        ----------
        model_source : ModelSource
            The model source containing data and equations.
        component_key : ComponentKey
            The key to identify components in the model source.
        """
        # NOTE: set
        self._model_source = model_source

        # SECTION: source
        self.source = Source(
            model_source=model_source,
            component_key=component_key
        )

    @property
    def pools(self) -> Dict[str, CustomProperty]:
        return self._pools

    @property
    def model_source(self) -> ModelSource:
        return self._model_source

    @property
    def required_keys(self) -> set:
        return self._required_keys

    # SECTION: CRUD operations for pools
    # NOTE: add to pool

    def add_to_pool(
            self,
            symbol: str,
            data: Dict[str, Any]
    ) -> bool:
        try:
            # NOTE: check if symbol already exists
            if symbol in self._pools:
                logger.warning(
                    f"Symbol '{symbol}' already exists in pools. Overwriting.")

            # NOTE: add to pools
            # >> check
            if not isinstance(data, dict):
                logger.error(
                    f"Data for symbol '{symbol}' must be a dictionary. Given type: {type(data)}")
                return False

            # > check keys: must include 'symbol', 'value', 'unit'
            required_keys = self.required_keys

            if not required_keys.issubset(data.keys()):
                logger.error(
                    f"Data for symbol '{symbol}' must include keys: {required_keys}. Given keys: {data.keys()}")
                return False

            # create CustomProperty instance
            try:
                custom_property = CustomProperty(
                    symbol=data['symbol'],
                    value=data['value'],
                    unit=data['unit']
                )
            except Exception as e:
                logger.error(
                    f"Error creating CustomProperty for symbol '{symbol}': {e}")
                return False

            self._pools[symbol] = custom_property
            logger.info(f"Added symbol '{symbol}' to pools.")
            return True
        except Exception as e:
            logger.error(f"Error adding symbol '{symbol}' to pools: {e}")
            return False

    # NOTE: add bulk to pool

    def add_bulk_to_pool(
            self,
            data_dict: Dict[str, Dict[str, Any]]
    ) -> bool:
        try:
            for symbol, data in data_dict.items():
                success = self.add_to_pool(symbol, data)
                if not success:
                    logger.warning(
                        f"Failed to add symbol '{symbol}' to pools. Continuing with next.")
            return True
        except Exception as e:
            logger.error(f"Error adding bulk symbols to pools: {e}")
            return False

    # NOTE: get from pool
    # ! get from pool by symbol
    def get_from_pool(
            self,
            symbol: str
    ) -> Optional[CustomProperty]:
        try:
            if symbol in self._pools:
                return self._pools[symbol]
            else:
                logger.warning(f"Symbol '{symbol}' not found in pools.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving symbol '{symbol}' from pools: {e}")
            return None

    # ! get from data source by symbol & component id, then from pool if not found

    def gt(
            self,
            symbol: str,
            component: Component,
            component_key: ComponentKey
    ) -> Optional[CustomProperty]:
        try:
            # NOTE: try to get from data source
            if self.source is not None:
                data_source = self.source.datasource
                if data_source is not None:
                    # >> component id
                    component_id = set_component_id(component, component_key)

                    # res
                    result = self.source.component_data_extractor(
                        component_id=component_id,
                    )

                    # >> check result
                    if result is not None:
                        return CustomProperty(
                            symbol=symbol,
                            value=result['value'],
                            unit=result['unit']
                        )

            # NOTE: if not found in data source, try to get from pool
            return self.get_from_pool(symbol)
        except Exception as e:
            logger.error(f"Error getting symbol '{symbol}': {e}")
            return None

    # NOTE: remove from pool

    def remove_from_pool(
            self,
            symbol: str
    ) -> bool:
        try:
            if symbol in self._pools:
                del self._pools[symbol]
                logger.info(f"Removed symbol '{symbol}' from pools.")
                return True
            else:
                logger.warning(f"Symbol '{symbol}' not found in pools.")
                return False
        except Exception as e:
            logger.error(f"Error removing symbol '{symbol}' from pools: {e}")
            return False

    # NOTE: clear pool

    def clear_pool(self) -> bool:
        try:
            self._pools.clear()
            logger.info("Cleared all symbols from pools.")
            return True
        except Exception as e:
            logger.error(f"Error clearing pools: {e}")
            return False
