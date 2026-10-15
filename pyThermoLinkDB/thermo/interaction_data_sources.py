# SECTION: Imports
# NOTE: Standard library
import logging
from collections.abc import Sequence
from typing import Any, Dict, List, Literal, Optional, cast

# NOTE: Third-party
from pyThermoDB.core import TableInteractionData
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    Mixture,
    MixtureKey,
)
from pythermodb_settings.utils import create_mixture_id

# NOTE: Local
from .source import Source
from .interaction_data_source import InteractionDataSourceCore


# NOTE: Module logger
logger = logging.getLogger(__name__)


# SECTION: Multiple interaction data sources
class InteractionDataSourcesCore:
    """Adapter for all registered interaction tables for one mixture."""

    def __init__(
        self,
        components: Mixture,
        source: Source,
        mixture_key: Optional[MixtureKey] = None,
        extract_list: Optional[list[str]] = None,
        delimiter: str = '|',
        case: Literal['lower', 'upper'] | None = None,
    ) -> None:
        # SECTION: Source configuration
        self.components = components
        self.source = source
        self.mixture_key = (
            mixture_key if mixture_key is not None else source.mixture_key
        )
        self.extract_list = extract_list
        self.delimiter = delimiter
        self.case = case

        # SECTION: Datasource registration identity
        # ! Canonicalization applies to this outer registration id only.
        self.mixture_name = create_mixture_id(
            components=self.components,
            mixture_key=self.mixture_key,
            delimiter=delimiter,
            case=case,
        )
        self.component_names = [
            component.strip()
            for component in self.mixture_name.split(delimiter)
        ]

        # SECTION: Interaction table extraction
        self.interaction_data = self._get_interaction_data()

        # ? Retain only explicitly requested registration keys when provided.
        if self.extract_list:
            extracted: Dict[str, TableInteractionData] = {}
            for prop_name in self.extract_list:
                interaction_source = self.interaction_data.get(prop_name)
                if interaction_source is None:
                    logger.warning(
                        "Interaction property '%s' is not available for "
                        "mixture '%s'.",
                        prop_name,
                        self.mixture_name,
                    )
                    continue
                extracted[prop_name] = interaction_source
            self.interaction_data = extracted

        # SECTION: Built singular sources
        self._props = self.all_props()
        self._props_symbols = self._all_props_symbols()
        self._src = self.build()

    # SECTION: Public properties
    @property
    def src(self) -> Dict[str, InteractionDataSourceCore]:
        return self._src

    @property
    def props(self) -> List[str]:
        return self.all_props()

    @property
    def props_symbols(self) -> List[str]:
        return self._all_props_symbols()

    # SECTION: Internal source extraction
    def _get_interaction_data(self) -> Dict[str, TableInteractionData]:
        try:
            # NOTE: mixture_name identifies the outer datasource registration.
            mixture_data = self.source.datasource.get(self.mixture_name)
            if mixture_data is None:
                logger.warning(
                    "Interaction data not found for mixture: %s",
                    self.mixture_name,
                )
                return {}
            if not isinstance(mixture_data, dict):
                logger.error(
                    "Datasource entry for mixture '%s' is not a dictionary.",
                    self.mixture_name,
                )
                return {}

            # ! Exclude ordinary scalar and matrix entries for this mixture.
            interaction_data = {
                name: value
                for name, value in mixture_data.items()
                if isinstance(value, TableInteractionData)
            }
            if not interaction_data:
                logger.warning(
                    "No TableInteractionData entries found for mixture: %s",
                    self.mixture_name,
                )
            return interaction_data
        except Exception as exc:
            logger.error("Error retrieving interaction data: %s", exc)
            return {}

    # SECTION: Metadata and availability
    def all_props(self) -> List[str]:
        return list(self.interaction_data.keys())

    def _all_props_symbols(self) -> List[str]:
        symbols: List[str] = []
        for interaction_source in self.interaction_data.values():
            symbols.extend(
                str(symbol)
                for symbol in interaction_source.interaction_symbol
            )

        # ! One table may be registered under several datasource keys.
        # ! Preserve symbol order while removing duplicates.
        return list(dict.fromkeys(symbols))

    def is_prop_available(self, name: str) -> bool:
        return name in self.interaction_data

    def check_availability(self, names: List[str]) -> Dict[str, bool]:
        return {name: name in self.interaction_data for name in names}

    def all_available(self, names: List[str]) -> bool:
        return all(self.check_availability(names).values())

    # SECTION: Singular source builder
    def build(self) -> Dict[str, InteractionDataSourceCore]:
        try:
            return {
                prop_name: InteractionDataSourceCore(
                    prop_name=prop_name,
                    components=self.components,
                    source=self.source,
                    mixture_key=cast(MixtureKey, self.mixture_key),
                    delimiter=self.delimiter,
                    case=cast(
                        Literal['lower', 'upper'] | None,
                        self.case,
                    ),
                )
                for prop_name in self.all_props()
            }
        except Exception as exc:
            logger.error("Error creating interaction data sources: %s", exc)
            return {}

    # SECTION: Build status
    def summary(self) -> Dict[str, bool]:
        if not self.extract_list:
            return {}
        return {
            prop_name: (
                prop_name in self._src
                and self._src[prop_name].build_status()
            )
            for prop_name in self.extract_list
        }

    def build_status(self) -> bool:
        if not self.extract_list:
            return True
        return all(self.summary().values())

    # SECTION: Singular source selection
    def select(self, name: str) -> Optional[InteractionDataSourceCore]:
        interaction_source = self._src.get(name)
        if interaction_source is None:
            logger.warning(
                "Interaction property '%s' not found for mixture '%s'.",
                name,
                self.mixture_name,
            )
        return interaction_source

    # SECTION: Raw table access
    def prop(self, name: str) -> Optional[TableInteractionData]:
        interaction_source = self.interaction_data.get(name)
        if interaction_source is None:
            logger.warning(
                "Interaction property '%s' not found for mixture '%s'.",
                name,
                self.mixture_name,
            )
        return interaction_source

    def interaction(self, name: str) -> Optional[TableInteractionData]:
        return self.prop(name)

    def get_interaction(self, name: str) -> Optional[TableInteractionData]:
        return self.prop(name)

    # SECTION: Table inspection and record filtering
    def table(
        self,
        name: str,
        mode: Literal['all', 'available'] = 'all',
    ) -> Optional[Any]:
        selected = self.select(name)
        return None if selected is None else selected.table(mode=mode)

    def structure(self, name: str) -> Optional[Any]:
        selected = self.select(name)
        return None if selected is None else selected.structure()

    def info(self, name: str) -> Optional[Dict[str, Any]]:
        selected = self.select(name)
        return None if selected is None else selected.info()

    def select_records(
        self,
        name: str,
        *,
        property_name: Optional[str] = None,
        contains: Optional[Sequence[str]] = None,
        order: Optional[int] = None,
        include_null: bool = False,
    ) -> Dict[Any, Any]:
        selected = self.select(name)
        if selected is None:
            return {}
        return selected.select(
            property_name=property_name,
            contains=contains,
            order=order,
            include_null=include_null,
        )

    # SECTION: Name-prefixed scalar and record facade
    def get(
        self,
        name: str,
        property_name: str,
        mixture: str | Sequence[str],
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
    ) -> Any:
        selected = self.select(name)
        if selected is None:
            return default
        return selected.get(
            property_name,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
        )

    def require(
        self,
        name: str,
        property_name: str,
        mixture: str | Sequence[str],
    ) -> Any:
        selected = self.select(name)
        if selected is None:
            return None
        return selected.require(property_name, mixture)

    def has(
        self,
        name: str,
        property_name: str,
        mixture: str | Sequence[str],
        *,
        require_value: bool = True,
    ) -> bool:
        selected = self.select(name)
        if selected is None:
            return False
        return selected.has(
            property_name,
            mixture,
            require_value=require_value,
        )

    def get_mixture(
        self,
        name: str,
        mixture: str | Sequence[str],
        *,
        include_null: bool = True,
    ) -> Dict[str, Any]:
        selected = self.select(name)
        if selected is None:
            return {}
        return selected.get_mixture(mixture, include_null=include_null)

    def get_property(
        self,
        name: str,
        property_name: str,
        *,
        include_null: bool = False,
    ) -> Dict[tuple[str, ...], Any]:
        selected = self.select(name)
        if selected is None:
            return {}
        return selected.get_property(
            property_name,
            include_null=include_null,
        )

    def interaction_order(
        self,
        name: str,
        mixture: str | Sequence[str],
    ) -> Optional[int]:
        selected = self.select(name)
        if selected is None:
            return None
        return selected.interaction_order(mixture)

    # SECTION: Compact interaction lookup facade
    def i(
        self,
        name: str,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
        message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        selected = self.select(name)
        if selected is None:
            return None
        return selected.i(
            property,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
            message=message,
        )

    def iis(
        self,
        name: str,
        property_name: str,
        mixtures: Optional[Sequence[str | Sequence[str]]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        include_null: bool = False,
        default: Any = None,
    ) -> Dict[tuple[str, ...], Any]:
        selected = self.select(name)
        if selected is None:
            return {}
        return selected.iis(
            property_name,
            mixtures,
            symmetric_groups=symmetric_groups,
            include_null=include_null,
            default=default,
        )

    # SECTION: Source-compatible aliases
    def interaction_value(
        self,
        name: str,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
    ) -> Any:
        selected = self.select(name)
        if selected is None:
            return default
        return selected.interaction_value(
            property,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
        )

    def interaction_i(
        self,
        name: str,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
        message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        return self.i(
            name,
            property,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
            message=message,
        )

    def interaction_property(
        self,
        name: str,
        property_name: str,
        *,
        include_null: bool = False,
    ) -> Dict[tuple[str, ...], Any]:
        return self.get_property(
            name,
            property_name,
            include_null=include_null,
        )

    # SECTION: Component-object lookup facade
    def get_from_components(
        self,
        name: str,
        property_name: str,
        components: Sequence[Any],
        *,
        component_key: Optional[ComponentKey] = None,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
    ) -> Any:
        selected = self.select(name)
        if selected is None:
            return default
        return selected.get_from_components(
            property_name,
            components,
            component_key=component_key,
            symmetric_groups=symmetric_groups,
            default=default,
        )

    def get_mixture_from_components(
        self,
        name: str,
        components: Sequence[Component],
        *,
        component_key: Optional[ComponentKey] = None,
        include_null: bool = True,
    ) -> Dict[str, Any]:
        selected = self.select(name)
        if selected is None:
            return {}
        return selected.get_mixture_from_components(
            components,
            component_key=component_key,
            include_null=include_null,
        )
