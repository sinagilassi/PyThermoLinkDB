# import packages/modules
import logging
from typing import Dict, Optional, Union, List, Any
from pyThermoDB import (
    TableMatrixData,
    TableData,
    TableEquation,
    TableConstants,
    CompBuilder
)
# local
# ! deps
from ..config.deps import get_config

# NOTE: logger
logger = logging.getLogger(__name__)


class ThermoLink:
    """
    ThermoLink class for linking thermodynamic data and equations from thermodb to a unified datasource.

    This class manages the integration of thermodynamic data and equations from a thermodb
    (thermodynamic database) into a unified data source. It provides functionality to:

    - Extract thermodynamic properties (data sources) from thermodb components
    - Extract thermodynamic equations from thermodb components
    - Extract thermodynamic constants from thermodb components
    - Apply symbol mapping and renaming based on rules defined in configuration files
    - Map components with custom naming conventions through rule-based transformations

    The class uses configuration-based rules to rename symbols and properties, allowing for
    flexible integration with different thermodb formats and naming conventions. It supports
    various data types including TableData, TableMatrixData, and TableEquation objects from
    the pyThermoDB library.

    Attributes
    ----------
    config : dict
        Configuration object loaded from config dependencies containing settings for
        symbol mapping rules and equation labeling behavior.
    original_equation_label : bool
        Flag indicating whether to use original equation labels or custom identifiers
        for equation symbols. Retrieved from the loaded configuration.

    Examples
    --------
    >>> # Create a ThermoLink instance and extract data sources
    >>> link = ThermoLink()
    >>> datasource = link._set_datasource(thermodb, rules, components)
    >>> equation_source = link._set_equationsource(thermodb, rules, components)

    Notes
    -----
    - This class is designed to work with thermodb objects from the pyThermoDB library
    - Rules for symbol renaming should follow the structure:
      {'COMPONENT_ID': {'DATA': {...}, 'EQUATIONS': {...}}}
    - Components must be present in the thermodb before attempting to extract data
    """

    def __init__(self):
        """
        Initialize the ThermoLink instance.

        Loads the configuration from dependencies and sets up the original_equation_label
        flag which controls whether equations use their original identifiers or custom
        return-based identifiers for symbol naming.

        Raises
        ------
        Exception
            If configuration loading fails or required configuration parameters are missing.

        Notes
        -----
        The configuration is loaded once during initialization and stored as an instance
        attribute for use throughout the object's lifetime.
        """
        # load reference
        # NOTE: get config
        self.config = get_config()
        # ! original equation label
        self.original_equation_label = self.config.original_equation_label

    # SECTION: set datasource
    # ! extract data source from thermodb and set symbol based on rules for each component (component id)
    def _set_datasource(
        self,
        thermodb: dict,
        thermodb_rule: dict,
        components: list
    ) -> dict:
        '''
        Extracts and constructs a unified data source from thermodb components.

        This method processes thermodynamic properties from specified components in the
        thermodb, applies symbol renaming rules, and returns a unified data structure.
        It handles multiple data types (TableData and TableMatrixData) and applies
        component-specific rules for symbol mapping.

        Parameters
        ----------
        thermodb : dict
            Dictionary containing thermodynamic database components. Each component
            should be a thermodb object with properties accessible via check_properties()
            and select() methods.
        thermodb_rule : dict
            Dictionary of rules for symbol renaming, structured as:
            {
                'COMPONENT_ID': {
                    'DATA': {
                        'old_symbol': 'new_symbol',
                        ...
                    }
                },
                ...
            }
            If a component is not in this dictionary, no renaming is applied.
        components : list
            List of component identifiers (strings) to process from thermodb.
            Only components present in both thermodb and this list are processed.

        Returns
        -------
        datasource : dict
            A nested dictionary with structure:
            {
                'COMPONENT_ID': {
                    'symbol': property_object,
                    ...
                },
                ...
            }
            Where property_object is a TableData or TableMatrixData object from pyThermoDB.

        Raises
        ------
        Exception
            If building the datasource fails, including cases where:
            - Matrix symbol is None when processing TableMatrixData
            - Unknown data types are encountered (logged as warning)

        Notes
        -----
        - Components not present in thermodb are silently skipped
        - Symbol renaming is applied based on both direct symbol names and column headers
        - None and 'None' string values are filtered out during processing
        - Logging is used to track warnings and informational messages
        - This is a private method intended for internal use within ThermoLink

        See Also
        --------
        _set_equationsource : For extracting equation sources
        _set_constantssource : For extracting constant sources
        '''
        try:
            # datasource
            datasource = {}

            # looping through each component
            for component in components:

                # NOTE: check if component is in thermodb
                if component in thermodb:
                    # init datasource for component
                    datasource[component] = {}

                    # ! saved component data
                    # check properties -> data
                    data = list(
                        thermodb[component].check_properties().keys()
                    )

                    # check
                    if len(data) != 0:

                        # NOTE: looping through each data source (GENERAL)
                        for src in data:
                            # REVIEW: get data
                            src_ = thermodb[component].select(src)

                            # init
                            df_src = None

                            # check
                            if isinstance(src_, TableData):
                                # NOTE: set
                                df_src = src_.data_structure()

                                # ? take all columns (header)
                                header = df_src['COLUMNS'].tolist()

                                # ? take all symbols
                                symbols = df_src['SYMBOL'].tolist()
                            elif isinstance(src_, TableMatrixData):
                                # NOTE: set
                                matrix_symbol_ = src_.matrix_symbol

                                # take all symbols
                                if matrix_symbol_ is None:
                                    raise Exception(
                                        'Matrix symbol is None, ',
                                        component
                                    )

                                # ? get all symbols
                                symbols = matrix_symbol_

                                # ? take all columns (header)
                                header = []
                            else:
                                # log
                                logger.warning(
                                    f'Unknown data type {type(src_)} for component {component}'
                                )
                                symbols = []
                                header = []

                            # looping through item data
                            # SECTION: looking through each symbol
                            for symbol in symbols:
                                # check
                                if (
                                    symbol is not None and
                                    symbol != 'None'
                                ):
                                    # ! symbol
                                    symbol = str(symbol).strip()

                                    # ? get property value
                                    # check if TableData or TableMatrixData
                                    _val = src_.get_property(symbol) if \
                                        isinstance(src_, TableData) else src_

                                    # NOTE: check symbol rename is required
                                    if component in thermodb_rule.keys():
                                        # get thermodb rule
                                        _rules = thermodb_rule[component].get(
                                            'DATA',
                                            None
                                        )

                                        # check
                                        if _rules:
                                            # set
                                            if symbol in _rules.keys():
                                                # ! rename
                                                symbol = _rules[symbol]

                                    # LINK: update
                                    datasource[component][symbol] = _val

                            # SECTION: looking through each header
                            if df_src is not None:
                                # looping through each header
                                for header_ in header:
                                    # check
                                    if header_ is not None and header_ != 'None':
                                        # ! header
                                        header_ = str(header_).strip()

                                        # ! header index
                                        header_index = df_src['COLUMNS'].tolist().\
                                            index(header_)

                                        # ? find symbol
                                        symbol_ = df_src['SYMBOL'].tolist()[
                                            header_index
                                        ]

                                        # ! check symbol if None and '' and 'None'
                                        if (
                                            symbol_ is None or
                                            symbol_ == '' or
                                            symbol_ == 'None'
                                        ):
                                            continue

                                        # NOTE: check already set
                                        # if symbol_ in datasource[component].keys():
                                        #     # skip
                                        #     continue

                                        _val = src_.get_property(symbol_) if \
                                            isinstance(src_, TableData) else src_

                                        # NOTE: check symbol rename is required
                                        if component in thermodb_rule.keys():
                                            # get thermodb rule
                                            _rules = thermodb_rule[component].get(
                                                'DATA',
                                                None
                                            )

                                            # check
                                            if _rules:
                                                # set
                                                if header_ in _rules.keys():
                                                    # ! rename
                                                    symbol_ = _rules[header_]

                                        # LINK: update
                                        datasource[component][symbol_] = _val
                    else:
                        # no data registered
                        logger.info(
                            f'No data registered for component {component}')
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)

    # SECTION: set equation source
    # ! extract equation source from thermodb and set symbol based on rules for each component (component id)
    def _set_equationsource(
        self,
        thermodb: dict,
        thermodb_rule: dict,
        components: list
    ) -> dict:
        '''
        Extracts and constructs a unified equation source from thermodb components.

        This method processes thermodynamic equations from specified components in the
        thermodb, applies symbol renaming rules, and returns a unified equation structure.
        It handles equation identification, symbol extraction, and rule-based transformations
        to map equations to their appropriate symbolic representations.

        Parameters
        ----------
        thermodb : dict
            Dictionary containing thermodynamic database components. Each component
            should be a thermodb object with equations accessible via check_functions()
            and select() methods.
        thermodb_rule : dict
            Dictionary of rules for equation symbol renaming, structured as:
            {
                'COMPONENT_ID': {
                    'EQUATIONS': {
                        'equation_identifier': 'new_symbol',
                        ...
                    }
                },
                ...
            }
            If a component is not in this dictionary, original equation identifiers
            are used (unless modified by return_identifier logic).
        components : list
            List of component identifiers (strings) to process from thermodb.
            Only components present in both thermodb and this list are processed.

        Returns
        -------
        datasource : dict
            A nested dictionary with structure:
            {
                'COMPONENT_ID': {
                    'symbol': equation_object,
                    ...
                },
                ...
            }
            Where equation_object is a TableEquation object from pyThermoDB.

        Raises
        ------
        Exception
            If building the equation source fails during processing.

        Notes
        -----
        - Equations are identified using equation identifiers from thermodb
        - Symbol mapping follows this priority:
          1. Direct equation_identifier match in rules
          2. Returned symbol match in rule values
          3. Return identifier (if original_equation_label is False and single return)
          4. Original equation identifier (if no rules apply)
        - Only TableEquation objects are processed; other types trigger warnings
        - Components not present in thermodb are silently skipped
        - This is a private method intended for internal use within ThermoLink
        - original_equation_label attribute controls symbol naming behavior

        See Also
        --------
        _set_datasource : For extracting data sources
        _set_constantssource : For extracting constant sources
        '''
        try:
            # datasource
            datasource = {}
            for component in components:
                if component in thermodb:
                    # set
                    datasource[component] = {}

                    # SECTION: setting based on key functions
                    # component registered data/equations
                    eq_data = list(
                        thermodb[component].check_functions().keys()
                    )

                    # check
                    if len(eq_data) != 0:
                        # looping through each equation data
                        for eq in eq_data:
                            # >> equation identifier
                            equation_identifier = str(eq).strip()
                            # ! initial symbol set
                            symbol = equation_identifier

                            # NOTE: select equation
                            _val = thermodb[component].select(eq)
                            # check
                            if not isinstance(_val, TableEquation):
                                logger.warning(
                                    f'Unknown equation type {type(_val)} for component {component}'
                                )
                                continue

                            # NOTE: get original symbol
                            original_symbols: list[str] = list(
                                _val.return_symbols.keys()
                            )

                            # NOTE: equation identifier
                            return_identifier = _val.make_identifiers(
                                param_id='return',
                                mode="symbol"
                            )

                            # ! set original symbol
                            returned_symbol = None
                            # >> only if one symbol
                            if len(original_symbols) > 0:
                                returned_symbol = original_symbols[0]

                            # NOTE: update equation symbol with rules
                            # ! check if component is in thermodb_rule
                            if component in thermodb_rule.keys():
                                # get thermodb rule
                                _rules = thermodb_rule[component].get(
                                    'EQUATIONS',
                                    None
                                )

                                # SECTION: verify _rules keys to set with equation identifier
                                if _rules:
                                    # ? keys (equation identifiers)
                                    keys_ = list(_rules.keys())
                                    # ? values (symbols)
                                    values_ = list(_rules.values())

                                    # NOTE: check & set symbol if found in rules
                                    if equation_identifier in keys_:
                                        # ! rename: use the symbol from rules (get value by key)
                                        symbol = str(
                                            _rules[equation_identifier]
                                        )
                                    else:
                                        # ! check returned_symbol if in values
                                        if (
                                            returned_symbol is not None and
                                            returned_symbol in values_
                                        ):
                                            # find key by value
                                            idx_ = values_.index(
                                                returned_symbol
                                            )
                                            # set symbol
                                            symbol = str(_rules[keys_[idx_]])
                                elif (
                                    len(return_identifier) == 1 and
                                    self.original_equation_label is False
                                ):
                                    # ! set symbol using return identifier
                                    symbol = str(return_identifier[0])
                                else:
                                    # log
                                    logger.warning(
                                        f'No matching rule found for equation {equation_identifier} of component {component}'
                                    )

                            # LINK: update
                            datasource[component][symbol] = _val
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)

    # SECTION: set constants source
    def _set_constantssource(
        self,
        thermodb: dict,
        thermodb_rule: dict,
        constants_id: Optional[str] = 'Constants'
    ) -> dict:
        '''
        Extracts and constructs a constants source from thermodb components.

        Parameters
        ----------
        thermodb: dict[str, CompBuilder]
            A dictionary representing the thermodynamic database, where keys are component
            identifiers and values are CompBuilder objects containing properties and equations.
        thermodb_rule: dict
            A dictionary containing rules for renaming symbols and properties.
        constants_id: str, optional
            The identifier used to locate constants in the thermodb. Default is 'Constants'.

        Returns
        -------
        constantssource: dict
            A dictionary mapping constant symbols to their corresponding constant tables.

        Notes
        -----
        - The thermodb_rule should contain appropriate mappings for constants and defined as follows:

        structured as:
            {
                'Constants: {
                    'CONSTANTS: {
                        'description-1': 'symbol-1',
                        'description-2': 'symbol-2',
                        ...
                    }
            }
        '''
        try:
            # NOTE: init constants source
            constantssource = {}

            # constants thermodb src
            constants_thermodb: Optional[Any] = None

            # >> check if constants_id is in thermodb
            if constants_id not in thermodb.keys():
                logger.warning(
                    f'Constants id {constants_id} not found in thermodb, skipping constants source extraction.'
                )
                return {}

            # NOTE: select constants thermodb (CompBuilder object)
            # select constants
            constants_thermodb: Optional[Any] = thermodb.get(
                constants_id, None
            )

            # NOTE: check if constants_thermodb is CompBuilder object
            if isinstance(constants_thermodb, CompBuilder):
                # ! get constants ids
                constants_src = constants_thermodb.check_constants()
                # >> check
                if len(constants_src) == 0:
                    logger.warning(
                        f'No constants found in thermodb for {constants_id}, skipping constants source extraction.'
                    )
                    return {}

                # ! get constants labels
                constants_labels: List[
                    Dict[str, str]
                ] | None = constants_thermodb.all_constants_id_labels()
                # >> check
                if constants_labels is None:
                    logger.warning(
                        f'No constants labels found in thermodb for {constants_id}, skipping constants source extraction.'
                    )
                    return {}

                # ! get constants identifiers
                constants_identifiers: List[
                    Dict[str, List[str]]
                ] | None = constants_thermodb.all_constants_identifiers()
                # >> check
                if constants_identifiers is None:
                    logger.warning(
                        f'No constants identifiers found in thermodb for {constants_id}, skipping constants source extraction.'
                    )
                    return {}

                # NOTE: get thermodb rule for constants
                _rules = thermodb_rule[constants_id].get(
                    'CONSTANTS',
                    None
                )

                # ! iterate through constants source
                for index, const_tb in enumerate(constants_src.values()):
                    # load all labels
                    identifiers_ = constants_identifiers[index]
                    # get first key of labels_ dict (description)
                    key_ = list(identifiers_.keys())[0]
                    # get labels list
                    labels_ = identifiers_[key_]

                    # check
                    if _rules:
                        # looping through each label
                        for label in labels_:
                            # check if label is in rules values
                            if label in _rules.values():
                                # set symbol
                                symbol = label

                                # LINK: update constantssource with symbol and constant table
                                constantssource[symbol] = const_tb.get_constant(
                                    constant=label,
                                    strict=False
                                )
                            else:
                                logger.warning(
                                    f'No matching rule found for constant label {label} in constants source, skipping this constant.'
                                )
                    else:
                        logger.warning(
                            f'No rules found for constants in thermodb, skipping symbol mapping for constants source.'
                        )
                        # LINK: update constantssource with original label and constant table
                        for label in labels_:
                            constantssource[label] = const_tb.get_constant(
                                constant=label,
                                strict=False
                            )
            else:
                logger.warning(
                    f'Constants thermodb for {constants_id} is not a CompBuilder object, skipping constants source extraction.'
                )
                return {}

            # res
            return constantssource
        except Exception as e:
            logger.error(f'Building constants source failed: {e}')
            return {}
