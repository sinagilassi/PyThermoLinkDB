# import libs
import logging
from typing import List, Dict, Optional, Any, Tuple, cast
from pyThermoDB.core import TableEquation
from pyThermoDB.models import EquationResult
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import set_component_id, build_component_mapper, is_component_key
from pyThermoLinkDB.models import ModelSource
# local
from ..config.constants import DATASOURCE, EQUATIONSOURCE, CONSTANTSSOURCE
from ..models.component_models import ComponentEquationSource

# logger
logger = logging.getLogger(__name__)


# SECTION: Source class

class Source:
    """
    Manager for model "datasource", "equationsource", and "constantssource"
    payloads used by PyThermoDB and pyThermoLinkDB.

    This class wraps an optional ModelSource and exposes a small API to:
    - access datasource, equationsource, and constantssource dictionaries,
    - access data, equation, and constants symbol metadata,
    - extract individual records for components, properties, and constants,
    - validate/build runtime argument dictionaries for equation execution,
    - construct and execute equation callables (via eq_builder and exec_eq).

    Responsibilities
    - Store and expose the parsed model_source payload (ModelSource.data_source, ModelSource.equation_source, and ModelSource.constants_source).
    - Provide safe extractors for component/property-level data, equations, and constants.
    - Provide helpers to build argument dictionaries from datasource entries and to validate argument requirements of TableEquation instances.
    - Provide higher-level equation-building (eq_builder) and execution (exec_eq) helpers that orchestrate TableEquation usage across components.

    Expected input structures (contracts)
    - model_source.data_source: dict mapping component_id -> symbol -> value (basic property values used to populate equation inputs).
    - model_source.equation_source: dict mapping component_id -> prop_name -> TableEquation-like object (must expose .args, .arg_symbols, .returns .return_symbols, .eq_num, .body, .cal).
    - model_source.constants_source: dict mapping constant_name -> value (or metadata dict) for source-level constants.

    Attributes
    - model_source (Optional[ModelSource]): Original model source object passed to the constructor.
    - component_key (ComponentKey): Default key format used to identify components.
    - _datasource (Optional[Dict[str, Any]]): Internal datasource dictionary or None when not provided.
    - _equationsource (Optional[Dict[str, Any]]): Internal equationsource dictionary or None when not provided.
    - _constantssource (Optional[Dict[str, Any]]): Internal constantssource dictionary or None when not provided.
    - _datasource_symbol (Optional[Dict[str, Any]]): Datasource symbol metadata from the model source.
    - _equationsource_symbol (Optional[Dict[str, Any]]): Equationsource symbol metadata from the model source.
    - _constantssource_symbol (Optional[Dict[str, Any]]): Constantssource symbol metadata from the model source.

    Public methods (high level)
    - datasource / equationsource / constantssource: properties returning the respective dict or an empty dict when not set.
    - datasource_symbols / equationsource_symbols / constantssource_symbols: properties returning source symbol metadata.
    - component_keys: property returning the supported component key formats.
    - set_source(model_source): parse/assign internal data, equation, and constants source dictionaries.
    - eq_extractor(component_id, prop_name): return a TableEquation for a component/property or None.
    - eq_symbol(component_id, prop_name): return equation symbol metadata for a component/property or None.
    - component_eq_extractor(component_id): return all equations for a component or None.
    - component_eq_symbols(component_id): return all equation symbol metadata for a component or None.
    - data_extractor(component_id, prop_name): return a datasource property dict or None.
    - data_symbol(component_id, prop_name): return datasource symbol metadata for a component/property or None.
    - get_prop(component_id, prop_name): alias for data_extractor.
    - get_prop_symbol(component_id, prop_name): alias for data_symbol.
    - constants_extractor(constant_name): return a constants source entry or None.
    - constant_symbol(constant_name): return constants source symbol metadata or None.
    - component_data_extractor(component_id): return datasource for a component or None.
    - component_data_symbols(component_id): return all datasource symbol metadata for a component or None.
    - get_dt(component_id): alias for component_data_extractor.
    - get_dt_symbols(component_id): alias for component_data_symbols.
    - const(constant_name): alias for constants_extractor.
    - const_symbol(constant_name): alias for constant_symbol.
    - check_args(component_id, args): validate that required args exist in the datasource and return the subset used for building inputs.
    - build_args(component_id, args, ignore_symbols=None): construct an input mapping for an equation using the datasource and optional ignored symbols.
    - eq_builder(components, prop_name, component_key, **kwargs): construct a mapping of component_id -> ComponentEquationSource ready for execution.
    - exec_eq(components, eq_src_comp, args_values=None, component_key, **kwargs): execute previously built equations and return results.
    - eval_eq(components, eq_src_comp, args_values=None, **kwargs): alias for exec_eq.
    - eq_eval(components, eq_src_comp, args_values=None, **kwargs): alias for exec_eq.
    - get_component_data(component_id, components, component_key): aggregate datasource and equationsource entries for a component.
    - is_prop_available / is_prop_eq_available / is_prop_data_available: availability checks across datasource and equationsource.
    - is_constant_available(constant_name): availability check across constantssource.

    Notes
    - The Source class is an adapter/utility and does not perform unit conversions or semantic harmonization of values between different sources.
    - Many methods return None on error and log via the module logger; callers should check for None and handle errors appropriately.
    - The class assumes a consistent structure for TableEquation-like objects and for datasource/equationsource/constantssource dictionaries as described above.
    """

    # NOTE: Attributes
    # ! component keys
    _component_keys: List[ComponentKey] = [
        'Name-State',
        'Formula-State',
        'Name-Formula',
        'Name-Formula-State',
        'Formula-Name-State'
    ]

    def __init__(
        self,
        model_source: Optional[ModelSource] = None,
        component_key: ComponentKey = 'Name-State',
        **kwargs
    ):
        '''
        Initialize the Source class.

        Parameters
        ----------
        model_source : Optional[ModelSource]
            The model source object containing datasource, equationsource, and constantssource dictionaries.
        component_key : Literal['Name-State', 'Formula-State', 'Name-Formula', 'Name', 'Formula', 'Name-Formula-State', 'Formula-Name-State']
            The key to identify the component, default is 'Name-State'.
        component_keys : Optional[List[ComponentKey]]
            List of component keys to build the equation for, default is None which means it will use the component_key defined in the Source class.

        '''
        # NOTE: set
        self.model_source: ModelSource | None = model_source
        self.component_key: ComponentKey = component_key

        # NOTE: source
        if model_source is None:
            # >>> set to None
            self._datasource = None
            self._equationsource = None
            self._constantssource = None
            # symbols
            self._datasource_symbol = None
            self._equationsource_symbol = None
            self._constantssource_symbol = None
        else:
            # >>> extract
            model_source_dict = {
                DATASOURCE: model_source.data_source,
                EQUATIONSOURCE: model_source.equation_source,
                CONSTANTSSOURCE: model_source.constants_source or {}
            }

            # ! set symbols
            self._datasource_symbol = model_source.data_symbols
            self._equationsource_symbol = model_source.equation_symbols
            self._constantssource_symbol = model_source.constants_symbols

            # ! set source
            (
                self._datasource,
                self._equationsource,
                self._constantssource
            ) = self.set_source(
                model_source=model_source_dict
            )

    # NOTE: repr
    def __repr__(self):
        '''String representation of the Source object.'''
        return f"Source(datasource={self.datasource}, equationsource={self.equationsource}, constantssource={self.constantssource}, component_keys={self.component_keys})"

    # SECTION: Properties
    # ! datasource
    @property
    def datasource(self) -> Dict[str, Any]:
        '''
        Get the datasource property.

        Returns
        -------
        dict
            The datasource dictionary.
        '''
        # NOTE: check if model source is valid
        if self._datasource is None:
            return {}
        return self._datasource

    # ! equationsource
    @property
    def equationsource(self) -> Dict[str, Any]:
        '''
        Get the equationsource property.

        Returns
        -------
        dict
            The equationsource dictionary.
        '''
        # NOTE: check if model source is valid
        if self._equationsource is None:
            return {}
        return self._equationsource

    # ! constantssource
    @property
    def constantssource(self) -> Dict[str, Any]:
        '''
        Get the constantssource property.

        Returns
        -------
        dict
            The constantssource dictionary.
        '''
        # NOTE: check if model source is valid
        if self._constantssource is None:
            return {}
        return self._constantssource

    # ! datasource symbols
    @property
    def datasource_symbols(self) -> Dict[str, Any]:
        '''
        Get the datasource symbols metadata.

        Returns
        -------
        dict
            The datasource symbols dictionary.
        '''
        if self._datasource_symbol is None:
            return {}
        return self._datasource_symbol

    # ! equationsource symbols
    @property
    def equationsource_symbols(self) -> Dict[str, Any]:
        '''
        Get the equationsource symbols metadata.

        Returns
        -------
        dict
            The equationsource symbols dictionary.
        '''
        if self._equationsource_symbol is None:
            return {}
        return self._equationsource_symbol

    # ! constantssource symbols
    @property
    def constantssource_symbols(self) -> Dict[str, Any]:
        '''
        Get the constantssource symbols metadata.

        Returns
        -------
        dict
            The constantssource symbols dictionary.
        '''
        if self._constantssource_symbol is None:
            return {}
        return self._constantssource_symbol

    # ! data symbols alias
    @property
    def data_symbols(self) -> Dict[str, Any]:
        '''
        Get the datasource symbols metadata.

        Alias for datasource_symbols.
        '''
        return self.datasource_symbols

    # ! equation symbols alias
    @property
    def equation_symbols(self) -> Dict[str, Any]:
        '''
        Get the equationsource symbols metadata.

        Alias for equationsource_symbols.
        '''
        return self.equationsource_symbols

    # ! constants symbols alias
    @property
    def constants_symbols(self) -> Dict[str, Any]:
        '''
        Get the constantssource symbols metadata.

        Alias for constantssource_symbols.
        '''
        return self.constantssource_symbols

    # ! component keys
    @property
    def component_keys(self) -> List[ComponentKey]:
        '''
        Get the component keys.

        Returns
        -------
        List[ComponentKey]
            The list of component keys.
        '''
        return self._component_keys

    @component_keys.setter
    def component_keys(self, keys: List[ComponentKey]):
        '''
        Set the component keys.

        Parameters
        ----------
        keys : List[ComponentKey]
            The list of component keys to set.
        '''
        if not isinstance(keys, list):
            logger.error("Component keys must be a list.")
            return

        for key in keys:
            if not is_component_key(key):
                logger.error(
                    f"Invalid component key: {key}. Must be one of {self._component_keys}.")
                return
        self._component_keys = keys

    # SECTION: Methods
    def set_source(
            self,
            model_source: Dict[str, Any]
    ):
        '''
        Set the model source.

        Parameters
        ----------
        model_source : Dict[str, Any]
            The model source dictionary.

        Returns
        -------
        tuple
            A tuple containing the datasource and equationsource dictionaries.
            - datasource : dict
            - equationsource : dict
            - constantssource : dict
        '''
        try:
            # NOTE: source
            # ! datasource
            _datasource = {
            } if model_source is None else model_source[DATASOURCE]

            # ! equationsource
            _equationsource = {
            } if model_source is None else model_source[EQUATIONSOURCE]

            # ! constantssource
            _constantssource = {
            } if model_source is None else model_source[CONSTANTSSOURCE]

            # res
            return _datasource, _equationsource, _constantssource
        except Exception as e:
            logger.error(f"Setting source failed: {e}")
            return None, None, None

    # SECTION: Extractors and helpers
    def eq_extractor(
        self,
        component_id: str,
        prop_name: str
    ) -> Optional[TableEquation]:
        '''
        Extracts the equilibrium property from the model source.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the property to extract.

        Returns
        -------
        TableEquation or None
            The extracted property.
        '''
        try:
            if self.equationsource is None:
                logger.warning("Equation source is None!")
                return None

            # NOTE: check component
            if component_id not in self.equationsource.keys():
                logger.error(
                    f"Component '{component_id}' not found in model source.")
                return None

            # NOTE: check property
            if prop_name not in self.equationsource[component_id].keys():
                logger.error(
                    f"Property '{prop_name}' not found in model source registered for {component_id}.")
                return None

            return self.equationsource[component_id][prop_name]
        except Exception as e:
            logger.error(f"Equation extraction failed: {e}")
            return None

    # SECTION: equation symbol extractor
    def eq_symbol(
        self,
        component_id: str,
        prop_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts equation symbol metadata from the model source.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the equation property to extract.

        Returns
        -------
        Dict[str, Any] or None
            The extracted equation symbol metadata.
        '''
        try:
            if component_id not in self.equationsource_symbols.keys():
                logger.error(
                    f"Component '{component_id}' not found in equation symbols.")
                return None

            if prop_name not in self.equationsource_symbols[component_id].keys():
                logger.error(
                    f"Property '{prop_name}' not found in equation symbols registered for {component_id}.")
                return None

            return self.equationsource_symbols[component_id][prop_name]
        except Exception as e:
            logger.error(f"Equation symbol extraction failed: {e}")
            return None

    # SECTION: component equation extractor
    def component_eq_extractor(
        self,
        component_id: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts the component equations from the model source.

        Parameters
        ----------
        component_id : str
            The id of the component.

        Returns
        -------
        Dict[str, Any] or None
            The extracted component equations.
        '''
        try:
            if self.equationsource is None:
                return None

            # NOTE: check component
            if component_id not in self.equationsource.keys():
                logger.error(
                    f"Component '{component_id}' not found in model source.")
                return None

            return self.equationsource[component_id]
        except Exception as e:
            logger.error(f"Component equation extraction failed: {e}")
            return None

    # SECTION: component equation symbols extractor
    def component_eq_symbols(
        self,
        component_id: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts component equation symbol metadata from the model source.

        Parameters
        ----------
        component_id : str
            The id of the component.

        Returns
        -------
        Dict[str, Any] or None
            The extracted component equation symbol metadata.
        '''
        try:
            if component_id not in self.equationsource_symbols.keys():
                logger.error(
                    f"Component '{component_id}' not found in equation symbols.")
                return None

            return self.equationsource_symbols[component_id]
        except Exception as e:
            logger.error(f"Component equation symbol extraction failed: {e}")
            return None

    # SECTION: data extractor
    def data_extractor(
            self,
            component_id: str,
            prop_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts the data property from the model source.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the property to extract.

        Returns
        -------
        Dict[str, Any] or None
            The extracted property.

        Notes
        -----
        The extracted property is a dictionary containing the following keys:
        - 'symbol': The symbol of the property.
        - 'property_name': The name of the property.
        - 'unit': The unit of the property.
        - 'value': The value of the property.
        - 'message': A message about the property.
        '''
        try:
            if self.datasource is None:
                return None

            # NOTE: check component
            if component_id not in self.datasource.keys():
                logger.error(
                    f"Component '{component_id}' not found in model datasource.")
                return None

            # NOTE: check property
            if prop_name not in self.datasource[component_id].keys():
                logger.error(
                    f"Property '{prop_name}' not found in model datasource registered for {component_id}.")
                return None

            return self.datasource[component_id][prop_name]
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return None

    # SECTION: data symbol extractor
    def data_symbol(
            self,
            component_id: str,
            prop_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts data symbol metadata from the model source.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the property to extract.

        Returns
        -------
        Dict[str, Any] or None
            The extracted data symbol metadata.
        '''
        try:
            if component_id not in self.datasource_symbols.keys():
                logger.error(
                    f"Component '{component_id}' not found in data symbols.")
                return None

            if prop_name not in self.datasource_symbols[component_id].keys():
                logger.error(
                    f"Property '{prop_name}' not found in data symbols registered for {component_id}.")
                return None

            return self.datasource_symbols[component_id][prop_name]
        except Exception as e:
            logger.error(f"Data symbol extraction failed: {e}")
            return None

    # SECTION: get property alias
    def get_prop(
            self,
            component_id: str,
            prop_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Get a specific component property from the datasource.

        Alias for data_extractor.
        '''
        return self.data_extractor(
            component_id=component_id,
            prop_name=prop_name
        )

    # SECTION: get property symbol alias
    def get_prop_symbol(
            self,
            component_id: str,
            prop_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Get a specific component property symbol from the datasource symbols.

        Alias for data_symbol.
        '''
        return self.data_symbol(
            component_id=component_id,
            prop_name=prop_name
        )

    # SECTION: constants extractor
    def constants_extractor(
            self,
            constant_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts the constant from the model source.

        Parameters
        ----------
        constant_name : str
            The name of the constant to extract.

        Returns
        -------
        Dict[str, Any] or None
            The extracted constant.
        '''
        try:
            if self.constantssource is None:
                return None

            # NOTE: check constant
            if constant_name not in self.constantssource.keys():
                logger.error(
                    f"Constant '{constant_name}' not found in model constants source.")
                return None

            return self.constantssource[constant_name]
        except Exception as e:
            logger.error(f"Constant extraction failed: {e}")
            return None

    # SECTION: constant symbol extractor
    def constant_symbol(
            self,
            constant_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts constant symbol metadata from the model source.

        Parameters
        ----------
        constant_name : str
            The name of the constant to extract.

        Returns
        -------
        Dict[str, Any] or None
            The extracted constant symbol metadata.
        '''
        try:
            if constant_name not in self.constantssource_symbols.keys():
                logger.error(
                    f"Constant '{constant_name}' not found in constants symbols.")
                return None

            return self.constantssource_symbols[constant_name]
        except Exception as e:
            logger.error(f"Constant symbol extraction failed: {e}")
            return None

    # SECTION: const alias
    def const(
            self,
            constant_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Get a constant from the constants source.

        Alias for constants_extractor.
        '''
        return self.constants_extractor(
            constant_name=constant_name
        )

    # SECTION: const symbol alias
    def const_symbol(
            self,
            constant_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Get a constant symbol from the constants source symbols.

        Alias for constant_symbol.
        '''
        return self.constant_symbol(
            constant_name=constant_name
        )

    # SECTION: component data extractor
    def component_data_extractor(
            self,
            component_id: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts the component data from the datasource.

        Parameters
        ----------
        component_id : str
            The id of the component.

        Returns
        -------
        Dict[str, Any] or None
            The extracted component data.
        '''
        try:
            if self.datasource is None:
                return None

            # NOTE: check component
            if component_id not in self.datasource.keys():
                logger.error(
                    f"Component '{component_id}' not found in model datasource.")
                return None

            return self.datasource[component_id]
        except Exception as e:
            logger.error(f"Component data extraction failed: {e}")
            return None

    # SECTION: component data symbols extractor
    def component_data_symbols(
            self,
            component_id: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Extracts component data symbol metadata from the datasource symbols.

        Parameters
        ----------
        component_id : str
            The id of the component.

        Returns
        -------
        Dict[str, Any] or None
            The extracted component data symbol metadata.
        '''
        try:
            if component_id not in self.datasource_symbols.keys():
                logger.error(
                    f"Component '{component_id}' not found in data symbols.")
                return None

            return self.datasource_symbols[component_id]
        except Exception as e:
            logger.error(f"Component data symbol extraction failed: {e}")
            return None

    # SECTION: get data alias
    def get_dt(
            self,
            component_id: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Get all datasource entries for a component.

        Alias for component_data_extractor.
        '''
        return self.component_data_extractor(
            component_id=component_id
        )

    # SECTION: get data symbols alias
    def get_dt_symbols(
            self,
            component_id: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Get all datasource symbol metadata for a component.

        Alias for component_data_symbols.
        '''
        return self.component_data_symbols(
            component_id=component_id
        )

    # SECTION: args checker and builder
    def check_args(
        self,
        component_id: str,
        args
    ) -> Dict[str, Any]:
        '''
        Checks equation args against datasource, returns required args used in calculation.

        Parameters
        ----------
        component_id : str
            The id of the component.
        args : tuple
            equation args

        Returns
        -------
        Dict[str, Any]
            The required args.

        Notes
        -----
        - The required args are those that are present in the datasource for the given component.
        - Default args "P" and "T" are always included.
        '''
        try:
            # NOTE: required args
            required_args = {}

            # datasource list
            datasource_component_list = list(
                self.datasource[component_id].keys()
            )

            # NOTE: default args
            datasource_component_list.append("P")
            datasource_component_list.append("T")

            # NOTE: check args within datasource
            for arg_key, arg_value in args.items():
                # symbol
                if arg_value['symbol'] in datasource_component_list:
                    # symbol
                    symbol_ = arg_value['symbol']
                    #  value
                    required_args[symbol_] = arg_value
                else:
                    raise Exception('Args not in datasource!')

            # res
            return required_args

        except Exception as e:
            raise Exception('Finding args failed!, ', e)

    # SECTION: args builder
    def build_args(
        self,
        component_id: str,
        args: Dict[str, Any],
        ignore_symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        '''
        Builds args from `datasource` for the given component, ignoring specified symbols.

        Parameters
        ----------
        component_id : str
            The id of the component.
        args : Dict[str, Any]
            The equation args containing name, symbol, and unit.
        ignore_symbols : list
            list of symbols to ignore, default is None but it can be defined as ["T", "P"]

        Returns
        -------
        Dict[str, Any]
            The built args dictionary.

        Notes
        -----
        - The built args dictionary contains the argument symbols as keys and their corresponding values from the datasource.
        - Symbols in the ignore_symbols list are skipped and set to None.
        - args units are automatically handled if provided.
        '''
        try:
            # SECTION: data source for component
            # check component in datasource
            if component_id not in self.datasource.keys():
                raise Exception('Component not in datasource!')

            # NOTE: component datasource
            component_datasource: dict = self.datasource[component_id]

            # SECTION: build args
            # >> empty dict
            if len(component_datasource) == 0:
                logger.warning("Component datasource is empty.")

                # iterate through args and set to None
                res = {
                    v['symbol']: {'value': None, 'symbol': v['symbol'], 'unit': v['unit']} for k, v in args.items()
                }

                return res

            # SECTION: build args and update from datasource
            # init res
            res = {}

            # looping through args
            # ! v contains name, symbol, unit
            for k, v in args.items():
                # symbol
                symbol = v['symbol']
                unit = v['unit']

                # NOTE: check if symbol is in ignore symbols
                if ignore_symbols is not None:
                    # ! check in ignore symbols
                    if symbol not in ignore_symbols:
                        # check in component database
                        for key, value in component_datasource.items():
                            if symbol == key:
                                res[symbol] = {
                                    # ? taken from datasource
                                    'value': value['value'],
                                    'symbol': symbol,
                                    'unit': unit
                                }

                    # ! check if not updated means external arg
                    if symbol not in res.keys():
                        # >> for external args which should be provided later
                        res[symbol] = {
                            'value': None,
                            'symbol': symbol,
                            'unit': unit
                        }

                else:
                    # ! check in component database
                    for key, value in component_datasource.items():
                        if symbol == key:
                            # update
                            # >> extract value
                            res[symbol] = {
                                # ? taken from datasource
                                'value': value['value'],
                                'symbol': symbol,
                                'unit': unit
                            }

                    # ! check if not updated means external arg
                    if symbol not in res.keys():
                        # >> for external args which should be provided later
                        res[symbol] = {
                            'value': None,
                            'symbol': symbol,
                            'unit': unit
                        }

            return res
        except Exception as e:
            raise Exception('Building args failed!, ', e)

    # SECTION: equation builder
    def eq_builder(
        self,
        components: List[Component],
        prop_name: str,
        component_key: Optional[ComponentKey] = None,
        component_keys: Optional[List[ComponentKey]] = None,
        **kwargs
    ) -> Optional[Dict[str, ComponentEquationSource]]:
        '''
        Builds the equation for the given components and property name.

        Parameters
        ----------
        components : List[Component]
            List of component to build the equation for.
        prop_name : str
            The name of the property to build the equation for.
        component_key : ComponentKey, optional
            The key to identify the component, default is None which means it will use the component_key defined in the Source class.
        component_keys : List[ComponentKey], optional
            List of component keys to build the equation for, default is None which means it will use the component_key defined in the Source class.
        **kwargs : dict
            Additional keyword arguments for the equation builder.

        Returns
        -------
        Dict[str, ComponentEquationSource] or None
            The built equation for each component which includes:
            - value: The equation value.
            - args: The equation arguments.
            - arg_symbols: The equation argument symbols.
            - returns: The equation returns.
            - return_symbols: The equation return symbols.

        Raises
        ------
        ValueError
            If the equation source is not defined or if the property name is empty.
        '''
        # NOTE: check if model source is valid
        if self.equationsource is None:
            raise ValueError("Equation source is not defined.")

        # SECTION: check component key
        # ! if component key is provided, use it, otherwise use the default component key defined in source
        selected_component_key = component_key if component_key is not None else self.component_key

        # NOTE: extract component ids
        component_ids = []
        for component in components:
            # set component id
            component_id = set_component_id(
                component=component,
                component_key=cast(ComponentKey, selected_component_key)
            )
            component_ids.append(component_id)

        # SECTION: component keys already defined in source, check if component keys are valid
        component_keys_missed: List[ComponentKey] = []

        # check component keys
        if component_keys is not None:
            for component_key in component_keys:
                # add component key to missed list if not in source component key
                if component_key != selected_component_key:
                    component_keys_missed.append(component_key)

        # SECTION: check property
        for component in component_ids:
            # check equation availability
            if prop_name not in self.equationsource[component].keys():
                logger.error(
                    f"Component '{component}' does not have property '{prop_name}' in model source.")
                return None

        # NOTE: property name
        if len(prop_name) == 0:
            raise ValueError("Property name cannot be empty.")

        # strip
        prop_name = prop_name.strip()

        # NOTE: vapor pressure source
        eq_src_comp = {}

        # looping through components
        for i, comp in enumerate(component_ids):
            # NOTE: equation source
            _eq = None
            # select equation [?]
            _eq = self.eq_extractor(comp, prop_name)
            # ! >> check
            if _eq is None:
                logger.warning(
                    f"Equation for property '{prop_name}' not found for component '{comp}'.")
                continue

            # NOTE: args
            _args = _eq.args
            # TODO: return only required args
            arg_mapping = self.check_args(
                comp,
                _args
            )

            # build args
            _input_args = self.build_args(
                component_id=comp,
                args=arg_mapping,
            )

            # NOTE: create equation builder result
            # ! number
            number_ = _eq.eq_num
            # ! body
            body_ = _eq.body
            # ! arg
            args_ = _eq.args if isinstance(_eq.args, dict) else {}
            arg_symbols_ = _eq.arg_symbols
            arg_identifiers = _eq.make_identifiers(
                param_id="arg",
                mode="symbol"
            )
            # ! returns
            returns_ = _eq.returns if isinstance(_eq.returns, dict) else {}
            return_symbols_ = _eq.return_symbols
            return_identifiers = _eq.make_identifiers(
                param_id="return",
                mode="symbol"
            )

            _res = ComponentEquationSource(
                source=_eq,
                inputs=_input_args,
                num=number_,
                fn=_eq.cal,
                body=body_,
                args=args_,
                arg_symbols=arg_symbols_,
                arg_identifiers=arg_identifiers,
                arg_mappings=arg_mapping,
                returns=returns_,
                return_symbols=return_symbols_,
                return_identifiers=return_identifiers
            )

            eq_src_comp[comp] = _res

            # ! >> check component keys missed and update
            if len(component_keys_missed) > 0:
                # build component mapper for missed keys
                mapper_ = build_component_mapper(
                    component=components[i],
                    component_keys=component_keys_missed
                )

                # get ids
                for id_ in mapper_.values():
                    eq_src_comp[id_] = _res

        # res
        return eq_src_comp

    # SECTION: equation executor
    def exec_eq(
        self,
        components: List[Component],
        eq_src_comp: Dict[str, ComponentEquationSource],
        args_values: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        '''
        Executes the equation for the given components and arguments.

        Parameters
        ----------
        components : List[Component]
            List of components to execute the equation for.
        eq_src_comp : Dict[str, ComponentEquationSource]
            Dictionary containing the equation source for each component.
        args_values : Dict[str, float]
            Dictionary containing the values for the arguments.
        **kwargs : dict
            Additional keyword arguments for the equation execution.

        Returns
        -------
        Tuple[List[float], Dict[str, Any]] or None
            - List of property results for each component.
            - Dictionary containing the results of the equation execution for each component.
        '''
        try:
            # NOTE: check if model source is valid
            if not isinstance(components, list):
                logger.error("Components must be a list.")
                return None

            # SECTION: component ids
            component_ids = []
            for component in components:
                # set component id
                component_id = set_component_id(
                    component=component,
                    component_key=cast(ComponentKey, self.component_key)
                )
                component_ids.append(component_id)

            # NOTE: check if eq_src_comp is a dictionary
            if not isinstance(eq_src_comp, dict):
                logger.error("Equation source must be a dictionary.")
                return None

            # NOTE: check if args_values is a dictionary
            if (
                args_values is not None and
                not isinstance(args_values, dict)
            ):
                logger.error("Arguments values must be a dictionary.")
                return None

            # NOTE: check if components are in eq_src_comp
            for component in component_ids:
                if component not in eq_src_comp:
                    logger.error(
                        f"Component '{component}' not found in equation source.")
                    return None

            # SECTION: execute equation
            # NOTE: init res
            prop_res = []
            prop_res_dict = {}

            # looping over components
            for i, component in enumerate(component_ids):
                # NOTE: equation [unit:?]
                eq_ = eq_src_comp[component].source
                args_ = eq_src_comp[component].inputs
                returns_ = eq_src_comp[component].returns
                # equation execution
                fn = eq_src_comp[component].fn

                # ! update args for any external values
                # args_['T'] = T
                if args_values is not None:
                    # NOTE: check if args_values is a dictionary
                    if not isinstance(args_values, dict):
                        logger.error("Arguments values must be a dictionary.")
                        return None

                    # NOTE: update args with args_values
                    for key, value in args_values.items():
                        # NOTE: check if key is in args
                        if key in args_:
                            # update
                            args_[key] = value

                # SECTION: cal
                # execute
                res_: EquationResult = fn(**args_)

                # >> extract
                res_value_ = res_['value']
                res_unit_ = res_['unit']

                # NOTE: return
                return_key_ = []
                return_val_ = []
                for key, value in returns_.items():
                    return_key_.append(key)
                    return_val_.append(value)

                # check length
                property_name = ''
                for key in return_key_:
                    if len(property_name) > 0:
                        property_name += ', '
                    property_name += key

                property_symbol = ''
                for val in return_val_:
                    if len(property_symbol) > 0:
                        property_symbol += ', '
                    property_symbol += str(val['symbol'])

                # save
                prop_res.append(res_value_)
                # dict type
                prop_res_dict[component] = {
                    "property_name": property_name,
                    "value": res_value_,
                    "unit": res_unit_,
                    "symbol": property_symbol,
                }

            # NOTE: results
            return prop_res, prop_res_dict
        except Exception as e:
            logger.error(f"Executing equation failed: {e}")
            return None

    # SECTION: equation evaluator alias
    def eval_eq(
        self,
        components: List[Component],
        eq_src_comp: Dict[str, ComponentEquationSource],
        args_values: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        '''
        Evaluate a previously built equation source.

        Alias for exec_eq.
        '''
        return self.exec_eq(
            components=components,
            eq_src_comp=eq_src_comp,
            args_values=args_values,
            **kwargs
        )

    # SECTION: equation evaluator alias
    def eq_eval(
        self,
        components: List[Component],
        eq_src_comp: Dict[str, ComponentEquationSource],
        args_values: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        '''
        Evaluate a previously built equation source.

        Alias for exec_eq.
        '''
        return self.exec_eq(
            components=components,
            eq_src_comp=eq_src_comp,
            args_values=args_values,
            **kwargs
        )

    # SECTION: get component data
    def get_component_data(
        self,
        component_id: str,
        components: List[Component],
        component_key: Optional[ComponentKey] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the component data from the datasource.

        Parameters
        ----------
        component_id : str
            The id of the component.
        components : List[str]
            List of available components.
        component_key : Optional[ComponentKey]
            The key to identify the component, default is None which means it will use the component_key defined in the Source class.

        Returns
        -------
        Dict[str, Any] or None
            The component data.
        """
        try:
            # check
            if not isinstance(component_id, str):
                logger.error("Component id must be a string.")
                return None

            # check available
            if not isinstance(components, list):
                logger.error("Components must be a list.")
                return None

            # SECTION: set component key
            selected_component_key = component_key if component_key is not None else self.component_key

            # SECTION: set component id
            component_ids = []
            for component in components:
                # set component id
                comp_id = set_component_id(
                    component=component,
                    component_key=cast(ComponentKey, selected_component_key)
                )
                component_ids.append(comp_id)

            if component_id not in component_ids:
                logger.error(
                    f"Component {component_id} is not available in the system.")
                return None

            # SECTION: collect data
            data = {}

            # check datasource
            if (
                self.datasource is not None and
                isinstance(self.datasource, dict)
            ):
                # add
                dt_ = self.datasource.get(component_id)
                if dt_ is not None:
                    data.update(dt_)

            # check equationsource
            if (
                self.equationsource is not None and
                isinstance(self.equationsource, dict)
            ):
                # add
                eq_ = self.equationsource.get(component_id)
                if eq_ is not None:
                    data.update(eq_)

            # get data
            return data
        except Exception as e:
            logger.error(f"Getting component data failed: {e}")
            return None

    # SECTION: check property availability
    def is_prop_available(
        self,
        component_id: str,
        prop_name: str
    ) -> bool:
        '''
        Check if the property is available for the given component either in datasource or equationsource.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the property to check.

        Returns
        -------
        bool
            True if the property is available, False otherwise.
        '''
        try:
            # SECTION: check equationsource
            if (
                self.equationsource is not None and
                isinstance(self.equationsource, dict)
            ):
                # check component
                if component_id in self.equationsource.keys():
                    # ! check property in equationsource
                    if prop_name in self.equationsource[component_id].keys():
                        return True

            # SECTION: check datasource
            if (
                self.datasource is not None and
                isinstance(self.datasource, dict)
            ):
                # check component
                if component_id in self.datasource.keys():
                    # ! check property in datasource
                    if prop_name in self.datasource[component_id].keys():
                        return True

            return False
        except Exception as e:
            logger.error(f"Checking property availability failed: {e}")
            return False

    # SECTION: check property equation availability
    def is_prop_eq_available(
        self,
        component_id: str,
        prop_name: str
    ) -> bool:
        '''
        Check if the property equation is available for the given component in equationsource.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the property to check.

        Returns
        -------
        bool
            True if the property equation is available, False otherwise.
        '''
        try:
            # SECTION: check equationsource
            if (
                self.equationsource is not None and
                isinstance(self.equationsource, dict)
            ):
                # check component
                if component_id in self.equationsource.keys():
                    # ! check property in equationsource
                    if prop_name in self.equationsource[component_id].keys():
                        return True

            return False
        except Exception as e:
            logger.error(
                f"Checking property equation availability failed: {e}")
            return False

    # SECTION: check property data availability
    def is_prop_data_available(
        self,
        component_id: str,
        prop_name: str
    ) -> bool:
        '''
        Check if the property data is available for the given component in datasource.

        Parameters
        ----------
        component_id : str
            The id of the component.
        prop_name : str
            The name of the property to check.

        Returns
        -------
        bool
            True if the property data is available, False otherwise.
        '''
        try:
            # SECTION: check datasource
            if (
                self.datasource is not None and
                isinstance(self.datasource, dict)
            ):
                # check component
                if component_id in self.datasource.keys():
                    # ! check property in datasource
                    if prop_name in self.datasource[component_id].keys():
                        return True

            return False
        except Exception as e:
            logger.error(f"Checking property data availability failed: {e}")
            return False

    # SECTION: check constants availability
    def is_constant_available(
        self,
        constant_name: str
    ) -> bool:
        '''
        Check if the constant is available in the constantssource.

        Parameters
        ----------
        constant_name : str
            The name of the constant to check.

        Returns
        -------
        bool
            True if the constant is available, False otherwise.
        '''
        try:
            # SECTION: check constantssource
            if (
                self.constantssource is not None and
                isinstance(self.constantssource, dict)
            ):
                # ! check constant in constantssource
                if constant_name in self.constantssource.keys():
                    return True

            return False
        except Exception as e:
            logger.error(f"Checking constant availability failed: {e}")
            return False
