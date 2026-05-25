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
    Runtime context for thermo property lookup and temporary property caching.

    A ``Context`` wraps a ``ModelSource`` and builds a ``Source`` helper to read
    component-linked data. It also maintains a property pool keyed by symbol,
    where each entry is stored as a ``CustomProperty``.

    Main responsibilities:
    - Access source-backed component data through ``self.source``.
    - Add/get/remove cached properties in ``pools``.
    - Resolve properties with ``gt(...)`` by checking source data first, then
    falling back to the pool.

    Notes:
    - ``_pools`` is defined at class level, so instances currently share the
    same pool unless this is refactored to an instance attribute.
    - Pool input requires ``symbol``, ``value``, and ``unit`` keys.
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
        Initialize the context with model and component-source configuration.

        Parameters
        ----------
        model_source : ModelSource
            Source definition that contains thermo data configuration.
        component_key : ComponentKey
            Component identifier strategy used by ``Source``.
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
        """
        Return the symbol-indexed property pool.

        Returns
        -------
        Dict[str, CustomProperty]
            Cached properties indexed by symbol.
        """
        return self._pools

    @property
    def model_source(self) -> ModelSource:
        """
        Return the configured model source.

        Returns
        -------
        ModelSource
            Source metadata used by this context.
        """
        return self._model_source

    @property
    def required_keys(self) -> set:
        """
        Return required keys for pool item payloads.

        Returns
        -------
        set
            Required payload keys: ``{'symbol', 'value', 'unit'}``.
        """
        return self._required_keys

    # SECTION: CRUD operations for pools
    # NOTE: add to pool

    def add(
            self,
            symbol: str,
            data: Dict[str, Any]
    ) -> bool:
        """
        Add or overwrite a single property in the pool.

        Parameters
        ----------
        symbol : str
            Pool key used to store the property.
        data : Dict[str, Any]
            Property payload containing ``symbol``, ``value``, and ``unit``.

        Returns
        -------
        bool
            ``True`` if stored successfully, otherwise ``False``.
        """
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

    def add_many(
            self,
            data_dict: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Add multiple properties to the pool.

        Parameters
        ----------
        data_dict : Dict[str, Dict[str, Any]]
            Mapping of pool symbols to property payloads.

        Returns
        -------
        bool
            ``True`` if the bulk process completes, ``False`` on fatal error.
            Individual item failures are logged and processing continues.
        """
        try:
            for symbol, data in data_dict.items():
                success = self.add(symbol, data)
                if not success:
                    logger.warning(
                        f"Failed to add symbol '{symbol}' to pools. Continuing with next.")
            return True
        except Exception as e:
            logger.error(f"Error adding bulk symbols to pools: {e}")
            return False

    # NOTE: get from pool
    # ! get from pool by symbol
    def get(
            self,
            symbol: str
    ) -> Optional[CustomProperty]:
        """
        Get a cached property by symbol.

        Parameters
        ----------
        symbol : str
            Property symbol key.

        Returns
        -------
        Optional[CustomProperty]
            Matching property if found, otherwise ``None``.
        """
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

    def resolve(
            self,
            symbol: str,
            component: Component,
            component_key: ComponentKey
    ) -> Optional[CustomProperty]:
        """
        Resolve a property from source data, then fall back to pool cache.

        Parameters
        ----------
        symbol : str
            Target property symbol.
        component : Component
            Component object used to build the component id.
        component_key : ComponentKey
            Key mode used by ``set_component_id``.

        Returns
        -------
        Optional[CustomProperty]
            Source-derived property when available; otherwise cached property
            from the pool; ``None`` if neither is found.
        """
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
            return self.get(symbol)
        except Exception as e:
            logger.error(f"Error getting symbol '{symbol}': {e}")
            return None

    # NOTE: remove from pool

    def remove(
            self,
            symbol: str
    ) -> bool:
        """
        Remove a property from the pool by symbol.

        Parameters
        ----------
        symbol : str
            Property symbol key.

        Returns
        -------
        bool
            ``True`` if removed, ``False`` if missing or on error.
        """
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

    def clear(self) -> bool:
        """
        Remove all cached properties from the pool.

        Returns
        -------
        bool
            ``True`` on success, otherwise ``False``.
        """
        try:
            self._pools.clear()
            logger.info("Cleared all symbols from pools.")
            return True
        except Exception as e:
            logger.error(f"Error clearing pools: {e}")
            return False
