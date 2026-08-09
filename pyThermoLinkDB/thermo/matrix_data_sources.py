import logging
from typing import Any, Dict, List, Literal, Optional, cast

from pyThermoDB.core import TableMatrixData
from pythermodb_settings.models import Component, ComponentKey, Mixture, MixtureKey
from pythermodb_settings.utils import create_mixture_id

from . import Source
from .matrix_data_source import MatrixDataSourceCore
from ..utils.mixture_tools import canonicalize_mixture_name


logger = logging.getLogger(__name__)


# SECTION: Multiple matrix data sources
class MatrixDataSourcesCore:
    """
    Core adapter for retrieving matrix data from a :class:`Source`.

    The class binds a mixture id to a source and exposes convenience methods
    around the underlying :class:`pyThermoDB.core.TableMatrixData` objects.
    """

    def __init__(
        self,
        components: Mixture,
        source: Source,
        mixture_key: Optional[MixtureKey] = None,
        extract_list: Optional[list[str]] = None,
        delimiter: str = '|',
        case: Literal['lower', 'upper'] | None = None,
    ) -> None:
        """
        Initialize MatrixDataSourceCore with mixture components and source.

        Parameters
        ----------
        components : Mixture
            Components used to generate the mixture id registered in the
            datasource.
        source : Source
            The source containing matrix data.
        mixture_key : Optional[MixtureKey]
            The key to identify mixtures in the source data. Defaults to the
            source mixture key.
        extract_list : Optional[list[str]]
            Optional list of matrix property names to retain.
        delimiter : str
            Delimiter used in the generated mixture id. Defaults to '|'.
        case : Literal['lower', 'upper'] | None
            Optional case normalization for mixture component names.
        """
        # NOTE: source identity and extraction settings for this one mixture.
        self.components = components
        self.source = source
        self.mixture_key = mixture_key if mixture_key is not None else source.mixture_key
        self.extract_list = extract_list
        self.delimiter = delimiter
        self.case = case

        # NOTE: create the mixture id from the components and mixture key
        # ! alphabetically sorted
        mixture_name = create_mixture_id(
            components=self.components,
            mixture_key=self.mixture_key,
            delimiter=delimiter,
            case=case,
        )

        #! mixture identity
        self.mixture_name = mixture_name
        #! component names
        self.component_names = [
            component.strip() for component in mixture_name.split(delimiter)
        ]

        # NOTE: retrieve the matrix data for the mixture from the source
        self.matrix_data: Dict[str, TableMatrixData] = self._get_matrix_data()

        # NOTE: apply the optional matrix property filter before building sources.
        if (
            self.matrix_data is not None and
            self.extract_list is not None and
            len(self.extract_list) > 0
        ):
            extracted_props: Dict[str, TableMatrixData] = {}

            for prop_name in self.extract_list:
                if not self.is_prop_available(prop_name):
                    logger.warning(
                        f"Matrix property '{prop_name}' is not available for mixture '{self.mixture_name}'."
                    )
                    continue

                extracted_props[prop_name] = self.matrix_data[prop_name]

            # set the matrix data to the extracted properties
            self.matrix_data = extracted_props

        #! built singular matrix sources
        self._props: List[str] = self.all_props()
        self._props_symbols: List[str] = self._all_props_symbols()
        self._src: Dict[str, MatrixDataSourceCore] = self.build()

    @property
    def src(self) -> Dict[str, MatrixDataSourceCore]:
        return self._src

    # SECTION: Alternate constructors
    @classmethod
    def from_mixture_name(
        cls,
        mixture_name: str,
        source: Source,
        extract_list: Optional[list[str]] = None,
        delimiter: str = '|',
        case: Literal['lower', 'upper'] | None = None,
    ) -> "MatrixDataSourcesCore":
        """
        Build a matrix data source from an already-resolved mixture id.

        Parameters
        ----------
        mixture_name : str
            Mixture id registered in the datasource. The id is canonicalized
            before lookup so differently ordered delimiter-separated component
            names can still resolve to the stored key when possible.
        source : Source
            Source object containing the datasource dictionary.
        extract_list : Optional[list[str]]
            Optional list of matrix property names to retain.
        delimiter : str
            Delimiter used to split and normalize ``mixture_name``.
        case : Literal['lower', 'upper'] | None
            Optional case normalization for the mixture id.

        Returns
        -------
            MatrixDataSourcesCore
            A matrix data source core bound to the resolved mixture id.
        """
        matrix_source = cls.__new__(cls)
        matrix_source.components = []
        matrix_source.source = source
        matrix_source.mixture_key = source.mixture_key
        matrix_source.extract_list = extract_list
        matrix_source.delimiter = delimiter
        matrix_source.case = case
        matrix_source.mixture_name, matrix_source.component_names = canonicalize_mixture_name(
            mixture_name=mixture_name,
            delimiter=delimiter,
            case=case,
        )
        matrix_source.matrix_data = matrix_source._get_matrix_data()

        if (
            matrix_source.matrix_data is not None and
            extract_list is not None and
            len(extract_list) > 0
        ):
            extracted_props: Dict[str, TableMatrixData] = {}

            for prop_name in extract_list:
                if not matrix_source.is_prop_available(prop_name):
                    logger.warning(
                        f"Matrix property '{prop_name}' is not available for mixture '{matrix_source.mixture_name}'."
                    )
                    continue

                extracted_props[prop_name] = matrix_source.matrix_data[prop_name]

            matrix_source.matrix_data = extracted_props

        matrix_source._props = matrix_source.all_props()
        matrix_source._props_symbols = matrix_source._all_props_symbols()

        return matrix_source

    # SECTION: Properties
    @property
    def props(self) -> List[str]:
        """
        Get matrix property names available for the mixture.

        Returns
        -------
        List[str]
            Matrix property keys such as ``['a', 'b', 'alpha']``.
        """
        return self.all_props()

    @property
    def props_symbols(self) -> List[str]:
        """
        Get matrix property symbols available for the mixture.

        Returns
        -------
        List[str]
            Matrix symbols reported by the underlying ``TableMatrixData``
            objects.
        """
        return self._all_props_symbols()

    # SECTION: Internal source extraction
    def _get_matrix_data(self) -> Dict[str, TableMatrixData]:
        """
        Retrieve all TableMatrixData entries for the mixture.

        Returns
        -------
        Dict[str, TableMatrixData]
            Mapping of matrix property name to its ``TableMatrixData`` object.
            Returns an empty dictionary when the mixture is missing or contains
            no matrix data entries.
        """
        try:
            # NOTE: extract the mixture data from the source's datasource dictionary
            mixture_data = self.source.datasource.get(self.mixture_name)

            if mixture_data is None:
                logger.warning(
                    f"Matrix data not found for mixture: {self.mixture_name}"
                )
                return {}

            if not isinstance(mixture_data, dict):
                logger.error(
                    f"Datasource entry for mixture '{self.mixture_name}' is not a dictionary."
                )
                return {}

            matrix_data: Dict[str, TableMatrixData] = {}
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

    # SECTION: Build and availability
    def summary(self) -> Dict[str, bool]:
        """
        Report extraction status for each requested matrix property.

        Returns
        -------
        Dict[str, bool]
            Mapping of each property in ``extract_list`` to whether it was
            found and retained. Returns an empty dictionary when no
            ``extract_list`` was supplied.
        """
        if not self.extract_list:
            return {}

        return {
            prop_name: (
                prop_name in self._src and
                self._src[prop_name].build_status()
            )
            for prop_name in self.extract_list
        }

    def build_status(self) -> bool:
        """
        Return whether every requested matrix property was extracted.

        Returns
        -------
        bool
            ``True`` when no extraction list was requested or every requested
            matrix property is available; otherwise ``False``.
        """
        if not self.extract_list:
            return True

        if self.extract_list:
            return all(self.summary().values())

        return all(matrix_source.build_status() for matrix_source in self._src.values())

    def build(self) -> Dict[str, MatrixDataSourceCore]:
        try:
            return {
                prop_name: MatrixDataSourceCore(
                    prop_name=prop_name,
                    components=self.components,
                    source=self.source,
                    mixture_key=cast(MixtureKey, self.mixture_key),
                    delimiter=self.delimiter,
                    case=cast(Literal['lower', 'upper'] | None, self.case),
                )
                for prop_name in self.all_props()
            }
        except Exception as e:
            logger.error(f"Error creating matrix data sources: {e}")
            return {}

    # SECTION: Metadata and availability helpers
    def all_props(self) -> List[str]:
        """
        Get all available matrix property names.

        Returns
        -------
        List[str]
            Property names available for the resolved mixture.
        """
        try:
            return list(self.matrix_data.keys())
        except Exception as e:
            logger.error(f"Error retrieving matrix property names: {e}")
            return []

    def _all_props_symbols(self) -> List[str]:
        """
        Get available matrix property symbols.

        Returns
        -------
        List[str]
            Flattened list of symbols from each available ``TableMatrixData``
            object's ``matrix_symbol`` metadata.
        """
        try:
            symbols: List[str] = []

            for matrix_data in self.matrix_data.values():
                matrix_symbols = matrix_data.matrix_symbol
                if isinstance(matrix_symbols, list):
                    symbols.extend(str(symbol) for symbol in matrix_symbols)

            return symbols
        except Exception as e:
            logger.error(f"Error retrieving matrix property symbols: {e}")
            return []

    def is_prop_available(self, name: str) -> bool:
        """
        Check whether a matrix property is available.

        Parameters
        ----------
        name : str
            Matrix property name to check.

        Returns
        -------
        bool
            ``True`` if ``name`` is available in ``matrix_data``; otherwise
            ``False``.
        """
        try:
            return name in self.matrix_data
        except Exception as e:
            logger.error(f"Error checking matrix property availability: {e}")
            return False

    def check_availability(self, names: List[str]) -> Dict[str, bool]:
        """
        Check availability for multiple matrix properties.

        Parameters
        ----------
        names : List[str]
            Matrix property names to check.

        Returns
        -------
        Dict[str, bool]
            Mapping of each requested name to its availability.
        """
        try:
            props_all = self.all_props()
            return {name: name in props_all for name in names}
        except Exception as e:
            logger.error(f"Error checking matrix property availability: {e}")
            return {name: False for name in names}

    def all_available(self, names: List[str]) -> bool:
        """
        Check whether all specified matrix properties are available.

        Parameters
        ----------
        names : List[str]
            Matrix property names to check.

        Returns
        -------
        bool
            ``True`` when all requested names are available; otherwise
            ``False``.
        """
        availability = self.check_availability(names=names)
        return all(availability.values())

    # SECTION: Raw and built source selection
    def prop(
        self,
        name: str,
    ) -> Optional[TableMatrixData]:
        """
        Get the raw TableMatrixData object for a matrix property.

        Parameters
        ----------
        name : str
            Matrix property name to retrieve.

        Returns
        -------
        Optional[TableMatrixData]
            The underlying matrix data table object, or ``None`` when the
            property is not available.
        """
        try:
            matrix_data = self.matrix_data.get(name)

            if matrix_data is None:
                logger.warning(
                    f"Matrix property '{name}' not found for mixture '{self.mixture_name}'."
                )
                return None

            return matrix_data
        except Exception as e:
            logger.error(f"Error retrieving matrix property '{name}': {e}")
            return None

    def matrix(
        self,
        name: str,
    ) -> Optional[TableMatrixData]:
        """
        Alias for ``prop``.

        Parameters
        ----------
        name : str
            Matrix property name to retrieve.

        Returns
        -------
        Optional[TableMatrixData]
            The underlying matrix data table object, or ``None`` when missing.
        """
        return self.prop(name=name)

    def get_matrix(
        self,
        name: str,
    ) -> Optional[TableMatrixData]:
        """
        Alias for ``prop``.

        Parameters
        ----------
        name : str
            Matrix property name to retrieve.

        Returns
        -------
        Optional[TableMatrixData]
            The underlying matrix data table object, or ``None`` when missing.
        """
        return self.prop(name=name)

    def select(
        self,
        symbol: str,
    ) -> Optional[MatrixDataSourceCore]:
        """
        Select a matrix property from the source.

        Parameters
        ----------
        symbol : str
            Matrix property symbol/name to retrieve.

        Returns
        -------
        Optional[MatrixDataSourceCore]
            The selected matrix data source, or ``None`` when unavailable.
        """
        matrix_source = self._src.get(symbol)
        if matrix_source is None:
            logger.warning(
                f"Matrix property '{symbol}' not found for mixture '{self.mixture_name}'."
            )
            return None

        return matrix_source

    # SECTION: Table inspection
    def table(
        self,
        name: str,
        mode: Literal['all', 'selected'] = 'all',
    ) -> Optional[Any]:
        """
        Get the matrix table for a matrix property.

        Parameters
        ----------
        name : str
            Matrix property name to retrieve.
        mode : Literal['all', 'selected']
            Table mode passed to ``TableMatrixData.get_matrix_table``.

        Returns
        -------
        Optional[Any]
            The matrix table, typically a pandas ``DataFrame``, or ``None`` if
            the property cannot be retrieved.
        """
        matrix_data: TableMatrixData | None = self.prop(name=name)
        if matrix_data is None:
            return None

        try:
            return matrix_data.get_matrix_table(mode=mode)
        except Exception as e:
            logger.error(f"Error retrieving matrix table '{name}': {e}")
            return None

    def structure(
        self,
        name: str,
    ) -> Optional[Any]:
        """
        Get the matrix data structure table for a matrix property.

        Parameters
        ----------
        name : str
            Matrix property name to inspect.

        Returns
        -------
        Optional[Any]
            The matrix data structure, typically a pandas ``DataFrame``, or
            ``None`` if the property cannot be retrieved.
        """
        matrix_data: TableMatrixData | None = self.prop(name=name)
        if matrix_data is None:
            return None

        try:
            return matrix_data.matrix_data_structure()
        except Exception as e:
            logger.error(f"Error retrieving matrix structure '{name}': {e}")
            return None

    # SECTION: Cell/property lookup
    def ij(
        self,
        name: str,
        property: str,
        symbol_format: Literal['alphabetic', 'numeric'] = 'alphabetic',
        message: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Any]:
        """
        Extract one i,j matrix value.

        Parameters
        ----------
        name : str
            Matrix property name registered in the datasource.
        property : str
            Property lookup string accepted by ``TableMatrixData.ij``, such as
            ``'alpha | methanol | ethanol'``.
        symbol_format : Literal['alphabetic', 'numeric']
            Matrix symbol format used by the underlying lookup.
        message : Optional[str]
            Optional message included in the returned data result.
        **kwargs : Any
            Additional keyword arguments forwarded to ``Source.matrix_ij``.

        Returns
        -------
        Optional[Any]
            Matrix lookup result from ``TableMatrixData.ij``, or ``None`` when
            the matrix property is unavailable.
        """
        return self.source.matrix_ij(
            mixture_name=self.mixture_name,
            prop_name=name,
            property=property,
            symbol_format=symbol_format,
            message=message,
            **kwargs,
        )

    def matrix_property(
        self,
        name: str,
        property: str,
        component_names: List[str],
        symbol_format: Literal['alphabetic', 'numeric'] = 'alphabetic',
        component_key: ComponentKey = 'Name',
        message: str = 'Get a component property from data table structure',
        **kwargs: Any,
    ) -> Optional[Any]:
        """
        Extract a matrix property for a component pair.

        Parameters
        ----------
        name : str
            Matrix property name registered in the datasource.
        property : str
            Matrix property symbol to extract, such as ``'alpha_i_j'``.
        component_names : List[str]
            Component pair used for the i,j lookup.
        symbol_format : Literal['alphabetic', 'numeric']
            Matrix symbol format used by the underlying lookup.
        component_key : ComponentKey
            Component identifier column used by the matrix table.
        message : str
            Message included in the returned data result.
        **kwargs : Any
            Additional keyword arguments forwarded to
            ``Source.matrix_property``.

        Returns
        -------
        Optional[Any]
            Matrix property result, or ``None`` when the property cannot be
            retrieved.
        """
        return self.source.matrix_property(
            mixture_name=self.mixture_name,
            prop_name=name,
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
        name: str,
        symbol_format: Literal['alphabetic', 'numeric'] = 'numeric',
        component_key: ComponentKey = 'Name',
    ) -> Optional[Any]:
        """
        Build a numeric or labelled matrix for a matrix property.

        Parameters
        ----------
        name : str
            Matrix property name registered in the datasource.
        symbol_format : Literal['alphabetic', 'numeric']
            Output format requested from ``TableMatrixData.mat``.
        component_key : ComponentKey
            Component key used for labelled matrix outputs.

        Returns
        -------
        Optional[Any]
            Matrix output from ``Source.mat``. Numeric output is typically a
            numpy array; labelled output is typically a dictionary.
        """
        return self.source.mat(
            mixture_name=self.mixture_name,
            prop_name=name,
            symbol_format=symbol_format,
            component_key=component_key,
            delimiter=self.delimiter,
            case=cast(Literal['lower', 'upper'] | None, self.case)
        )

    def matX(
        self,
        name: str,
        components: List[Component],
        symbol_format: Literal['alphabetic', 'numeric'] = 'numeric',
        component_key: ComponentKey = 'Name',
        mixture_key: Optional[MixtureKey] = None,
    ) -> Optional[Any]:
        """
        Build a numeric or labelled matrix using Component objects.

        Parameters
        ----------
        name : str
            Matrix property name registered in the datasource.
        components : List[Component]
            Components used by ``Source.matX`` to build and label the matrix.
        symbol_format : Literal['alphabetic', 'numeric']
            Output format requested from ``TableMatrixData.matX``.
        component_key : ComponentKey
            Component key used for labelled matrix outputs.
        mixture_key : Optional[MixtureKey]
            Mixture key used to derive the mixture id. Defaults to the source
            mixture key when omitted.

        Returns
        -------
        Optional[Any]
            Matrix output from ``Source.matX``. Numeric output is typically a
            numpy array; labelled output is typically a dictionary.
        """
        return self.source.matX(
            prop_name=name,
            components=components,
            symbol_format=symbol_format,
            component_key=cast(ComponentKey, component_key),
            mixture_key=mixture_key,
            delimiter=self.delimiter,
            case=cast(Literal['lower', 'upper'] | None, self.case)
        )
