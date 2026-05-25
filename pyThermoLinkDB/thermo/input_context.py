# import libs
import logging
from typing import Optional, Dict, Any
from pythermodb_settings.models import CustomProperty
# locals
from ..models.source import ModelSource

# NOTE: logger setup
logger = logging.getLogger(__name__)


class Context:

    # NOTE: attributes
    pools: Dict[str, CustomProperty] = {}

    # ! required keys
    _required_keys = {'symbol', 'value', 'unit'}

    def __init__(
            self,
            model_source: ModelSource
    ):
        # NOTE: set
        self._model_source = model_source

        # SECTION: extract
        # ! data source
        self._data_source = model_source.data_source
        # ! equation source
        self._equation_source = model_source.equation_source
        # ! data symbol
        self._data_symbols = model_source.data_symbols
        # ! equation symbol
        self._equation_symbols = model_source.equation_symbols

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
            if symbol in self.pools:
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

            self.pools[symbol] = custom_property
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

    def get_from_pool(
            self,
            symbol: str
    ) -> Optional[CustomProperty]:
        try:
            if symbol in self.pools:
                return self.pools[symbol]
            else:
                logger.warning(f"Symbol '{symbol}' not found in pools.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving symbol '{symbol}' from pools: {e}")
            return None

    # NOTE: remove from pool

    def remove_from_pool(
            self,
            symbol: str
    ) -> bool:
        try:
            if symbol in self.pools:
                del self.pools[symbol]
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
            self.pools.clear()
            logger.info("Cleared all symbols from pools.")
            return True
        except Exception as e:
            logger.error(f"Error clearing pools: {e}")
            return False
