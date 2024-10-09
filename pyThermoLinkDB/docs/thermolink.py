# THERMO LINK

# import packages/modules

# local


class ThermoLink:

    def __init__(self):
        # load reference
        pass

    def _build_datasource(self, thermodb, thermodb_rule, components, reference, ref_key='DEPENDANT-DATA'):
        '''
        Builds a datasource

        Parameters
        ----------
        components : list
            list of components
        reference : dict
            dict data of the reference
        ref_key : str, optional
            reference key, by default 'DEPENDANT-DATA'

        Returns
        -------
        datasource : dict
            datasource
        '''
        try:
            # check reference
            if reference is None or reference == 'None':
                raise Exception('Empty reference!')

            # reference
            # get all dependent data
            dependent_data_src = reference[str(ref_key).strip()]
            dependent_data = []
            # check
            if dependent_data_src is not None:
                for item, value in dependent_data_src.items():
                    _item_symbol = value['symbol']
                    dependent_data.append(_item_symbol)

            # datasource
            datasource = {}
            for component in components:
                if component in thermodb:
                    # set
                    datasource[component] = {}
                    # parms
                    for item in dependent_data:
                        # check property src
                        check_property_src = 'GENERAL'
                        # check
                        if component in thermodb_rule.keys():
                            # property source
                            check_property_src = thermodb_rule[component][item][0]

                        # val
                        _val = thermodb[component].check_property(
                            check_property_src).get_property(str(item).strip())
                        # unit conversion

                        datasource[component][item] = _val
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)

    def _build_equationsource(self,  thermodb, thermodb_rule, components, reference, ref_key='DEPENDANT-EQUATIONS'):
        '''
        Build datasource

        Parameters
        ----------
        components : list
            list of components
        reference : dict
            dict data of the reference

        Returns
        -------
        datasource : dict
            datasource
        '''
        try:
            # check reference
            if reference is None or reference == 'None':
                raise Exception('Empty reference!')

            # reference
            # get all dependent data
            dependent_data_src = reference[str(ref_key).strip()]
            dependent_data = []
            # check
            if dependent_data_src is not None and dependent_data_src != 'None':
                for item, value in dependent_data_src.items():
                    _item_symbol = value['symbol']
                    dependent_data.append(_item_symbol)

            # datasource
            datasource = {}
            for component in components:
                if component in thermodb:
                    # set
                    datasource[component] = {}
                    # parms
                    for item in dependent_data:
                        # check property src
                        check_property_src = None
                        # check
                        if component in thermodb_rule.keys():
                            # property source
                            check_property_src = thermodb_rule[component][item][0]

                            # val
                            _val = thermodb[component].check_function(
                                check_property_src)
                            # unit conversion

                            datasource[component][item] = _val
            # res
            return datasource
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)
