# SECTION: Imports
# NOTE: Standard library
import logging
from collections.abc import Sequence
from typing import Any, Dict, List, Literal, Optional

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
from ..models.mixture_models import InteractionDataSource


# NOTE: Module logger
logger = logging.getLogger(__name__)


# SECTION: Singular interaction data source
class InteractionDataSourceCore:
    """Adapter for one registered interaction-data table for one mixture.

    ``prop_name`` identifies the table in the datasource. It is intentionally
    separate from the scalar symbols stored inside ``TableInteractionData``
    because datasource rules may rename the registered key.
    """

    def __init__(
        self,
        prop_name: str,
        components: Mixture,
        source: Source,
        mixture_key: Optional[MixtureKey] = None,
        delimiter: str = '|',
        case: Literal['lower', 'upper'] | None = None,
    ) -> None:
        # SECTION: Source configuration
        self.prop_name = prop_name
        self.components = components
        self.source = source
        self.mixture_key = (
            mixture_key if mixture_key is not None else source.mixture_key
        )
        self.delimiter = delimiter
        self.case = case

        # SECTION: Datasource registration identity
        # ! Canonicalize only the outer datasource id. Interaction records
        # ! inside TableInteractionData must retain their declared order.
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
        # NOTE: Keep every registered interaction key for availability checks.
        self.interaction_data: Dict[str, TableInteractionData] = (
            self._get_interaction_data()
        )

        # ? Build the typed view for the one requested registration key.
        self._interaction_data_source = self._get_interaction_data_source()

        # NOTE: Cache the raw table for the public facade methods.
        self._interaction: Optional[TableInteractionData] = (
            self._interaction_data_source.source
            if self._interaction_data_source is not None
            else None
        )

        # ! A singular core is built only when its registered key resolves.
        self._status = self._interaction_data_source is not None

    # SECTION: Public properties
    @property
    def status(self) -> bool:
        return self._status

    @property
    def interaction_source(self) -> Optional[TableInteractionData]:
        return self._interaction

    @property
    def interaction_data_source(self) -> Optional[InteractionDataSource]:
        return self._interaction_data_source

    @property
    def props(self) -> List[str]:
        return self.all_props()

    @property
    def props_symbols(self) -> List[str]:
        if self._interaction is None:
            return []
        return list(dict.fromkeys(
            str(symbol) for symbol in self._interaction.interaction_symbol
        ))

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

            # ! Ignore ordinary scalar and matrix entries registered beside
            # ! interaction tables for the same mixture.
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

    def _get_interaction_data_source(
        self,
    ) -> Optional[InteractionDataSource]:
        # NOTE: prop_name may be a rules-based alias such as psi_ternary.
        interaction_source = self.interaction_data.get(self.prop_name)
        if interaction_source is None:
            logger.warning(
                "Interaction property '%s' not found for mixture '%s'.",
                self.prop_name,
                self.mixture_name,
            )
            return None

        return InteractionDataSource(
            source=interaction_source,
            interaction_symbol=[
                str(symbol)
                for symbol in interaction_source.interaction_symbol
            ],
            mixture_name=self.mixture_name,
            prop_name=self.prop_name,
            component_names=self.component_names,
        )

    # SECTION: Build status and availability
    def summary(self) -> Dict[str, bool]:
        return {self.prop_name: self.status}

    def build_status(self) -> bool:
        return self.status

    def all_props(self) -> List[str]:
        return list(self.interaction_data.keys())

    def is_prop_available(self, name: Optional[str] = None) -> bool:
        if name is None:
            return self.status
        return name in self.interaction_data

    def check_availability(self, names: List[str]) -> Dict[str, bool]:
        return {name: name in self.interaction_data for name in names}

    def all_available(self, names: List[str]) -> bool:
        return all(self.check_availability(names).values())

    # SECTION: Raw table access
    def prop(self) -> Optional[TableInteractionData]:
        return self._interaction

    def interaction(self) -> Optional[TableInteractionData]:
        return self.prop()

    def get_interaction(self) -> Optional[TableInteractionData]:
        return self.prop()

    # SECTION: Table inspection
    def table(
        self,
        mode: Literal['all', 'available'] = 'all',
    ) -> Optional[Any]:
        if self._interaction is None:
            return None
        try:
            return self._interaction.get_interaction_table(mode=mode)
        except Exception as exc:
            logger.error(
                "Error retrieving interaction table '%s': %s",
                self.prop_name,
                exc,
            )
            return None

    def structure(self) -> Optional[Any]:
        if self._interaction is None:
            return None
        try:
            return self._interaction.interaction_data_structure()
        except Exception as exc:
            logger.error(
                "Error retrieving interaction structure '%s': %s",
                self.prop_name,
                exc,
            )
            return None

    def info(self) -> Optional[Dict[str, Any]]:
        if self._interaction is None:
            return None
        try:
            return self._interaction.get_interaction_data_info()
        except Exception as exc:
            logger.error(
                "Error retrieving interaction info '%s': %s",
                self.prop_name,
                exc,
            )
            return None

    # SECTION: Scalar and record lookup facade
    def get(
        self,
        property_name: str,
        mixture: str | Sequence[str],
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
    ) -> Any:
        if self._interaction is None:
            return default
        return self._interaction.get(
            property_name,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
        )

    def require(
        self,
        property_name: str,
        mixture: str | Sequence[str],
    ) -> Any:
        if self._interaction is None:
            logger.error(
                "Interaction source '%s' is unavailable.", self.prop_name
            )
            return None
        return self._interaction.require(property_name, mixture)

    def has(
        self,
        property_name: str,
        mixture: str | Sequence[str],
        *,
        require_value: bool = True,
    ) -> bool:
        if self._interaction is None:
            return False
        return self._interaction.has(
            property_name,
            mixture,
            require_value=require_value,
        )

    def get_mixture(
        self,
        mixture: str | Sequence[str],
        *,
        include_null: bool = True,
    ) -> Dict[str, Any]:
        if self._interaction is None:
            return {}
        return self._interaction.get_mixture(
            mixture,
            include_null=include_null,
        )

    def get_property(
        self,
        property_name: str,
        *,
        include_null: bool = False,
    ) -> Dict[tuple[str, ...], Any]:
        if self._interaction is None:
            return {}
        return self._interaction.get_property(
            property_name,
            include_null=include_null,
        )

    def select(
        self,
        *,
        property_name: Optional[str] = None,
        contains: Optional[Sequence[str]] = None,
        order: Optional[int] = None,
        include_null: bool = False,
    ) -> Dict[Any, Any]:
        if self._interaction is None:
            return {}
        return self._interaction.select(
            property_name=property_name,
            contains=contains,
            order=order,
            include_null=include_null,
        )

    def interaction_order(
        self,
        mixture: str | Sequence[str],
    ) -> Optional[int]:
        if self._interaction is None:
            return None
        return self._interaction.interaction_order(mixture)

    # SECTION: Compact interaction lookup facade
    def i(
        self,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
        message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if self._interaction is None:
            return None
        return self._interaction.i(
            property,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
            message=message,
        )

    def iis(
        self,
        property_name: str,
        mixtures: Optional[Sequence[str | Sequence[str]]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        include_null: bool = False,
        default: Any = None,
    ) -> Dict[tuple[str, ...], Any]:
        if self._interaction is None:
            return {}
        return self._interaction.iis(
            property_name,
            mixtures,
            symmetric_groups=symmetric_groups,
            include_null=include_null,
            default=default,
        )

    # SECTION: Source-compatible aliases
    def interaction_value(
        self,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
    ) -> Any:
        result = self.i(
            property,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
        )
        if result is None:
            return default
        return result.get('value', default)

    def interaction_i(
        self,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
        message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        return self.i(
            property,
            mixture,
            symmetric_groups=symmetric_groups,
            default=default,
            message=message,
        )

    def interaction_property(
        self,
        property_name: str,
        *,
        include_null: bool = False,
    ) -> Dict[tuple[str, ...], Any]:
        return self.get_property(
            property_name,
            include_null=include_null,
        )

    # SECTION: Component-object lookup facade
    def get_from_components(
        self,
        property_name: str,
        components: Sequence[Any],
        *,
        component_key: Optional[ComponentKey] = None,
        symmetric_groups: Optional[Sequence[Sequence[int]]] = None,
        default: Any = None,
    ) -> Any:
        if self._interaction is None:
            return default
        return self._interaction.get_from_components(
            property_name,
            components,
            component_key=component_key,
            symmetric_groups=symmetric_groups,
            default=default,
        )

    def get_mixture_from_components(
        self,
        components: Sequence[Component],
        *,
        component_key: Optional[ComponentKey] = None,
        include_null: bool = True,
    ) -> Dict[str, Any]:
        if self._interaction is None:
            return {}
        return self._interaction.get_mixture_from_components(
            components,
            component_key=component_key,
            include_null=include_null,
        )
