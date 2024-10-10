# THERMO LINK

# import packages/modules

# local


class ThermoLink:

    def __init__(self):
        # load reference
        pass

    def _set_datasource(self, thermodb: dict, thermodb_rule: dict, components: list) -> dict:
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
            for component in components:
                if component in thermodb:
                    # set
                    datasource[component] = {}

                    # component registered data/equations
                    data = list(
                        thermodb[component].check_properties().keys())

                    # check
                    if len(data) != 0:
                        # looping through each data source (GENERAL)
                        for src in data:
                            # take data
                            df_src = thermodb[component].check_property(
                                src).data_structure()
                            # take all symbols
                            symbols = df_src['SYMBOL'].tolist()
                            # looping through item data
                            for symbol in symbols:
                                # check
                                if symbol is not None and symbol != 'None':
                                    # symbol
                                    symbol = str(symbol).strip()
                                    # val
                                    _val = thermodb[component].check_property(
                                        src).get_property(str(symbol).strip())

                                    # check symbol rename is required
                                    if symbol in thermodb_rule[component]['DATA']:
                                        # rename
                                        symbol = thermodb_rule[component]['DATA'][symbol]

                                    # update
                                    datasource[component][symbol] = _val
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)

    def _set_equationsource(self, thermodb: dict, thermodb_rule: dict, components: list) -> dict:
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

                    # component registered data/equations
                    eq_data = list(
                        thermodb[component].check_functions().keys())

                    # check
                    if len(eq_data) != 0:
                        # parms
                        for eq in eq_data:
                            # get function structure
                            # eq_str = thermodb[component].get_function(
                            #     eq).eq_structure(1)

                            # symbol
                            symbol = str(eq).strip()
                            # val
                            _val = thermodb[component].check_function(
                                eq)

                            # check symbol rename is required
                            if symbol in thermodb_rule[component]['EQUATIONS']:
                                # rename
                                symbol = thermodb_rule[component]['EQUATIONS'][symbol]

                            datasource[component][symbol] = _val
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)
