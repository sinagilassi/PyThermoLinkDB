# import packages/modules
import logging
from pyThermoDB import TableMatrixData, TableData, TableEquation
# local

# NOTE: logger
logger = logging.getLogger(__name__)


class ThermoLink:

    def __init__(self):
        # load reference
        pass

    def _set_datasource(
        self,
        thermodb: dict,
        thermodb_rule: dict,
        components: list
    ) -> dict:
        '''
        Sets a datasource

        Parameters
        ----------
        thermodb : dict
            thermodb
        thermodb_rule : dict
            thermodb rule
        components : list
            list of components

        Returns
        -------
        datasource : dict
            datasource
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
                                if symbol is not None and symbol != 'None':
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
                        raise Exception(
                            'No data registered in thermodb, ', component)
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)

    def _set_equationsource(
        self,
        thermodb: dict,
        thermodb_rule: dict,
        components: list
    ) -> dict:
        '''
        Sets equation source

        Parameters
        ----------
        thermodb : dict
            thermodb
        thermodb_rule : dict
            thermodb rule
        components : list
            list of components

        Returns
        -------
        datasource : dict
            datasource
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

                            # NOTE: update equation symbol with rules
                            # check if component is in thermodb_rule
                            if component in thermodb_rule.keys():
                                # get thermodb rule
                                _rules = thermodb_rule[component].get(
                                    'EQUATIONS',
                                    None
                                )

                                # NOTE: verify _rules keys to set with equation identifier
                                if _rules:
                                    # ! keys (equation identifiers)
                                    keys_ = _rules.keys()
                                    # set
                                    if equation_identifier in keys_:
                                        # rename: use the symbol from rules
                                        symbol = _rules[equation_identifier]
                            # else:
                            #     # ! use original symbols
                            #     if len(original_symbols) > 0:
                            #         symbol = original_symbols[0]

                            # LINK: update
                            datasource[component][symbol] = _val
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)
