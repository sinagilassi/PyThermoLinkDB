# import libs
import logging
from typing import List, Dict, Optional, Any, Tuple, Literal, cast
from pyThermoDB.core import TableEquation
from pyThermoDB.models import EquationResult
from pythermodb_settings.models import Component
from pythermodb_settings.utils import set_component_id
from pyThermoLinkDB.models import ModelSource
# local
from ..config.constants import DATASOURCE, EQUATIONSOURCE
from ..models.component_models import ComponentEquationSource

# logger
logger = logging.getLogger(__name__)


# SECTION: Source class

class Source:
    '''
    Source to manage datasource and equationsource built by PyThermoDB and PyThermoLinkDB.
    '''
    # NOTE: variables

    def __init__(
        self,
        model_source: Optional[ModelSource] = None,
        **kwargs
    ):
        '''Initialize the Source class.'''
        # NOTE: set
        self.model_source = model_source

        # NOTE: source
        if model_source is None:
            self._datasource = None
            self._equationsource = None
        else:
            # >> extract
            model_source_dict = {
                DATASOURCE: model_source.data_source,
                EQUATIONSOURCE: model_source.equation_source
            }

            # reset
            (
                self._datasource,
                self._equationsource
            ) = self.set_source(
                model_source=model_source_dict
            )

    def __repr__(self):
        return f"Source(datasource={self.datasource}, equationsource={self.equationsource})"

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

    def set_source(self, model_source: Dict[str, Any]):
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
        '''
        try:
            # NOTE: source
            # datasource
            _datasource = {
            } if model_source is None else model_source[DATASOURCE]

            # equationsource
            _equationsource = {
            } if model_source is None else model_source[EQUATIONSOURCE]

            # res
            return _datasource, _equationsource
        except Exception as e:
            logger.error(f"Setting source failed: {e}")
            return None, None

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

    def check_args(
        self,
        component_id: str,
        args
    ):
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
        list
            The required args.

        Notes
        -----
        - The required args are those that are present in the datasource for the given component.
        - Default args "P" and "T" are always included.
        '''
        try:
            # NOTE: required args
            required_args = []

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
                    # update
                    required_args.append(arg_value)
                else:
                    raise Exception('Args not in datasource!')

            # res
            return required_args

        except Exception as e:
            raise Exception('Finding args failed!, ', e)

    def build_args(
        self,
        component_id: str,
        args,
        ignore_symbols: Optional[List[str]] = None
    ):
        '''
        Builds args from `datasource` for the given component, ignoring specified symbols.

        Parameters
        ----------
        component_id : str
            The id of the component.
        args : tuple
            equation args
        ignore_symbols : list
            list of symbols to ignore, default is None but it can be defined as ["T", "P"]
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
                res = {arg['symbol'].strip(): None for arg in args}

                return res

            # SECTION: build args and update from datasource
            # init res
            res = {}

            # looping through args
            for arg in args:
                # symbol
                symbol = arg['symbol']

                # NOTE: check if symbol is in ignore symbols
                if ignore_symbols is not None:
                    # ! check in ignore symbols
                    if symbol not in ignore_symbols:
                        # check in component database
                        for key, value in component_datasource.items():
                            if symbol == key:
                                res[symbol] = value
                            else:
                                # default None
                                res[symbol] = None
                else:
                    # ! check in component database
                    for key, value in component_datasource.items():
                        if symbol == key:
                            # update
                            # >> extract value
                            res[symbol] = value
                        else:
                            # default None
                            # >> for external args which should be provided later
                            res[symbol] = None
            return res
        except Exception as e:
            raise Exception('Building args failed!, ', e)

    def eq_builder(
        self,
        components: List[Component],
        prop_name: str,
        component_key: Literal[
            'Name-State',
            'Formula-State',
            'Name',
            'Formula',
            'Name-Formula-State',
            'Formula-Name-State'
        ] = 'Name-State',
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
        component_key : Literal['Name-State', 'Formula-State', 'Name', 'Formula', 'Name-Formula-State', 'Formula-Name-State']
            The key to identify the component, default is 'Name-State'.
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
        '''
        # NOTE: check if model source is valid
        if self.equationsource is None:
            raise ValueError("Equation source is not defined.")

        # NOTE: extract component ids
        component_ids = []
        for component in components:
            # set component id
            component_id = set_component_id(
                component=component,
                component_key=component_key
            )
            component_ids.append(component_id)

        # NOTE: check property
        for component in component_ids:
            # check equation availability
            if prop_name not in self.equationsource[component].keys():
                raise ValueError(
                    f"Property '{prop_name}' not found in model source registered for {component}.")

        # NOTE: property name
        if len(prop_name) == 0:
            raise ValueError("Property name cannot be empty.")

        # strip
        prop_name = prop_name.strip()

        # NOTE: vapor pressure source
        eq_src_comp = {}

        # looping through components
        for component in component_ids:
            # NOTE: equation source
            _eq = None
            # select equation [?]
            _eq = self.eq_extractor(component, prop_name)
            # ! >> check
            if _eq is None:
                logger.warning(
                    f"Equation for property '{prop_name}' not found for component '{component}'.")
                continue

            # NOTE: args
            _args = _eq.args
            # check args (SI)
            _args_required = self.check_args(
                component,
                _args
            )

            # build args
            _input_args = self.build_args(
                component_id=component,
                args=_args_required,
            )

            # NOTE: update P and T
            # _args_['T'] = None
            # _args_['P'] = None

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
                returns=returns_,
                return_symbols=return_symbols_,
                return_identifiers=return_identifiers
            )

            eq_src_comp[component] = _res

        # res
        return eq_src_comp

    def exec_eq(
        self,
        components: List[Component],
        eq_src_comp: Dict[str, ComponentEquationSource],
        args_values: Optional[Dict[str, float]] = None,
        component_key: Literal[
            'Name-State',
            'Formula-State',
            'Name',
            'Formula',
            'Name-Formula-State',
            'Formula-Name-State'
        ] = 'Name-State',
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
        component_key : Literal['Name-State', 'Formula-State', 'Name', 'Formula', 'Name-Formula-State', 'Formula-Name-State']
            The key to identify the component, default is 'Name-State'.
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
                    component_key=component_key
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

    def get_component_data(
        self,
        component_id: str,
        components: List[Component],
        component_key: Literal[
            'Name-State',
            'Formula-State',
            'Name',
            'Formula',
            'Name-Formula-State',
            'Formula-Name-State'
        ] = 'Name-State',
    ) -> Optional[Dict[str, Any]]:
        """
        Get the component data from the datasource.

        Parameters
        ----------
        component_id : str
            The id of the component.
        components : List[str]
            List of available components.
        component_key : Literal['Name-State', 'Formula-State', 'Name', 'Formula', 'Name-Formula-State', 'Formula-Name-State']
            The key to identify the component, default is 'Name-State'.

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

            # SECTION: set component id
            component_ids = []
            for component in components:
                # set component id
                comp_id = set_component_id(
                    component=component,
                    component_key=component_key
                )
                component_ids.append(comp_id)

            if component_id not in component_ids:
                logger.error(
                    f"Component {component_id} is not available in the system.")
                return None

            # data
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
