import logging
from typing import Any, Dict, List, Literal, Optional, cast

from pyThermoDB.core import TableMatrixData
from pythermodb_settings.models import Component, Mixture, ComponentKey, MixtureKey
from pythermodb_settings.utils import create_mixture_id

from . import Source
from ..models.mixture_models import MixtureMatrixDataSource


logger = logging.getLogger(__name__)


# SECTION: Singular matrix data source
class MatrixDataSourceCore:
    """
    Core adapter for retrieving one matrix data property for one mixture.

    The requested matrix property name is
    bound during initialization, and access methods operate on that bound
    property without requiring callers to pass the name repeatedly.
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
        # NOTE: bind the requested matrix property to this single source.
        self.prop_name = prop_name
        self.components = components
        self.source = source
        self.mixture_key = mixture_key if mixture_key is not None else source.mixture_key
        self.delimiter = delimiter
        self.case = case

        # NOTE: resolve the mixture id once so all accessors use the same key.
        # ! sorted alphabetically by default
        self.mixture_name = create_mixture_id(
            components=self.components,
            mixture_key=self.mixture_key,
            delimiter=delimiter,
            case=case,
        )

        # parse component names from the resolved mixture id for later use
        self.component_names = [
            component.strip() for component in self.mixture_name.split(delimiter)
        ]

        # ! selected matrix data source model
        self.matrix_data = self._get_matrix_data()

        # ? retrieve the selected matrix data source for the requested property
        self.mixture_matrix_data_source: Optional[
            MixtureMatrixDataSource
        ] = self._get_matrix_data_source()

        # ? store the selected matrix data source for the requested property
        self._matrix: TableMatrixData | None = (
            self.mixture_matrix_data_source.source
            if self.mixture_matrix_data_source is not None
            else None
        )

        # NOTE: build status follows whether the selected property exists.
        self._status = self.mixture_matrix_data_source is not None

    # SECTION: Properties
    @property
    def status(self) -> bool:
        return self._status

    @property
    def matrix_source(self) -> Optional[TableMatrixData]:
        return self._matrix

    @property
    def matrix_data_source(self) -> Optional[MixtureMatrixDataSource]:
        return self.mixture_matrix_data_source

    # SECTION: Source model builder
    def _get_matrix_data_source(self) -> Optional[MixtureMatrixDataSource]:
        """
        Retrieve the matrix data source for the requested property name, matrix_data holds all available properties for the resolved mixture.
        """
        # ! retrieve the property from the matrix data dictionary
        matrix_source:  TableMatrixData | None = self.matrix_data.get(
            self.prop_name
        )

        # >> check
        if matrix_source is None:
            logger.warning(
                f"Matrix property '{self.prop_name}' not found for mixture '{self.mixture_name}'."
            )
            return None

        # get the matrix symbols from the source
        matrix_symbol = matrix_source.matrix_symbol
        if not isinstance(matrix_symbol, list):
            matrix_symbol = []

        return MixtureMatrixDataSource(
            source=matrix_source,
            matrix_symbol=matrix_symbol,
            mixture_name=self.mixture_name,
            prop_name=self.prop_name,
            component_names=self.component_names,
        )

    # SECTION: Availability and summary
    @property
    def props(self) -> List[str]:
        return self.all_props()

    @property
    def props_symbols(self) -> List[str]:
        return self._all_props_symbols()

    def summary(self) -> Dict[str, bool]:
        return {self.prop_name: self.status}

    def build_status(self) -> bool:
        return self.status

    def all_props(self) -> List[str]:
        try:
            return list(self.matrix_data.keys())
        except Exception as e:
            logger.error(f"Error retrieving matrix property names: {e}")
            return []

    def is_prop_available(self) -> bool:
        return self.status

    # SECTION: Raw matrix access
    # ! prop
    def prop(self) -> Optional[TableMatrixData]:
        return self._matrix

    # ! matrix
    def matrix(self) -> Optional[TableMatrixData]:
        return self.prop()

    # ! get_matrix
    def get_matrix(self) -> Optional[TableMatrixData]:
        return self.prop()

    # SECTION: Table inspection
    def table(
        self,
        mode: Literal['all', 'selected'] = 'all',
    ) -> Optional[Any]:
        if self._matrix is None:
            return None

        try:
            return self._matrix.get_matrix_table(mode=mode)
        except Exception as e:
            logger.error(
                f"Error retrieving matrix table '{self.prop_name}': {e}")
            return None

    def structure(self) -> Optional[Any]:
        if self._matrix is None:
            return None

        try:
            return self._matrix.matrix_data_structure()
        except Exception as e:
            logger.error(
                f"Error retrieving matrix structure '{self.prop_name}': {e}")
            return None

    # SECTION: Cell/property lookup
    def ij(
        self,
        property: str,
        symbol_format: Literal['alphabetic', 'numeric'] = 'alphabetic',
        message: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Any]:
        return self.source.matrix_ij(
            mixture_name=self.mixture_name,
            prop_name=self.prop_name,
            property=property,
            symbol_format=symbol_format,
            message=message,
            **kwargs,
        )

    def matrix_property(
        self,
        property: str,
        component_names: List[str],
        symbol_format: Literal['alphabetic', 'numeric'] = 'alphabetic',
        component_key: ComponentKey = 'Name',
        message: str = 'Get a component property from data table structure',
        **kwargs: Any,
    ) -> Optional[Any]:
        return self.source.matrix_property(
            mixture_name=self.mixture_name,
            prop_name=self.prop_name,
            property=property,
            component_names=component_names,
            symbol_format=symbol_format,
            component_key=component_key,
            message=message,
            **kwargs,
        )

    # SECTION: Matrix builders
    def mat(
        self,
        symbol_format: Literal['alphabetic', 'numeric'] = 'numeric',
        component_key: ComponentKey = 'Name',
    ) -> Optional[Any]:
        return self.source.mat(
            mixture_name=self.mixture_name,
            prop_name=self.prop_name,
            symbol_format=symbol_format,
            component_key=component_key,
            delimiter=self.delimiter,
            case=cast(Literal['lower', 'upper'] | None, self.case),
        )

    def matX(
        self,
        components: List[Component],
        symbol_format: Literal['alphabetic', 'numeric'] = 'numeric',
        component_key: ComponentKey = 'Name',
        mixture_key: Optional[MixtureKey] = None,
    ) -> Optional[Any]:
        return self.source.matX(
            prop_name=self.prop_name,
            components=components,
            symbol_format=symbol_format,
            component_key=component_key,
            mixture_key=mixture_key,
            delimiter=self.delimiter,
            case=cast(Literal['lower', 'upper'] | None, self.case),
        )

    # SECTION: Internal source extraction
    def _get_matrix_data(self) -> Dict[str, TableMatrixData]:
        """
        Retrieve the matrix data dictionary for the resolved mixture name. All properties available for that mixture are returned as a dictionary of property name to TableMatrixData entries. If the mixture is not found or the data is not in the expected format, an empty dictionary is returned.
        """
        try:
            mixture_data = self.source.datasource.get(self.mixture_name)

            # >> check
            if mixture_data is None:
                logger.warning(
                    f"Matrix data not found for mixture: {self.mixture_name}"
                )
                return {}

            # >> check type
            if not isinstance(mixture_data, dict):
                logger.error(
                    f"Datasource entry for mixture '{self.mixture_name}' is not a dictionary."
                )
                return {}

            # >>> filter for TableMatrixData entries
            matrix_data: Dict[str, TableMatrixData] = {}

            # iterate over the mixture data and extract TableMatrixData entries
            for prop_name, prop_data in mixture_data.items():
                if isinstance(prop_data, TableMatrixData):
                    matrix_data[prop_name] = prop_data

            if not matrix_data:
                logger.warning(
                    f"No TableMatrixData entries found for mixture: {self.mixture_name}"
                )

            return matrix_data
        except Exception as e:
            logger.error(f"Error retrieving matrix data: {e}")
            return {}

    # SECTION: Internal metadata helpers
    def _all_props_symbols(self) -> List[str]:
        try:
            if self._matrix is None:
                return []

            matrix_symbols = self._matrix.matrix_symbol
            if isinstance(matrix_symbols, list):
                return [str(symbol) for symbol in matrix_symbols]

            return []
        except Exception as e:
            logger.error(f"Error retrieving matrix property symbols: {e}")
            return []
