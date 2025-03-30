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
            
            # looping through each component
            for component in components:
                
                # NOTE: check if component is in thermodb
                if component in thermodb:
                    # init datasource for component
                    datasource[component] = {}

                    # saved component data
                    data = list(
                        thermodb[component].check_properties().keys())

                    # check
                    if len(data) != 0:
                        
                        # NOTE: looping through each data source (GENERAL)
                        for src in data:
                            # REVIEW: get data
                            df_src = thermodb[component].select_property(
                                src).data_structure()
                            
                            # take all symbols
                            symbols = df_src['SYMBOL'].tolist()
                            # looping through item data
                            for symbol in symbols:
                                # check
                                if symbol is not None and symbol != 'None':
                                    # ! symbol
                                    symbol = str(symbol).strip()
                                    # ! val (retrieve data from thermodb object using symbol)
                                    # old format
                                    _val = thermodb[component].select_property(
                                        src).get_property(symbol)
                                    
                                    # new format
                                    # _val0 = (thermodb[component]).retrieve(f"{src} | {symbol}")
                                    
                                    # NOTE: check symbol rename is required
                                    if symbol in thermodb_rule[component]['DATA']:
                                        # rename
                                        symbol = thermodb_rule[component]['DATA'][symbol]

                                    # update
                                    datasource[component][symbol] = _val
                    else:
                        # no data registered
                        raise Exception(
                            'No data registered in thermodb, ', component)
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
                            _val = thermodb[component].select_function(
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
