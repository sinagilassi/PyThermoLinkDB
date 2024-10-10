# THERMODB

# import packages/modules
import pyThermoDB
import os
import yaml
# local
from .thermolink import ThermoLink


class ThermoDBHub(ThermoLink):
    # vars
    _thermodb = {}
    _thermodb_rule = {}
    _hub = {}

    def __init__(self):
        # init super class
        ThermoLink().__init__()

    @property
    def thermodb(self):
        return self._thermodb

    @property
    def thermodb_rule(self):
        return self._thermodb_rule

    @property
    def hub(self):
        return self._hub

    def get_components(self):
        '''
        Gets a component list

        Parameters
        ----------
        None

        Returns
        -------
        components : list
            list of components
        '''
        try:
            components = list(self._thermodb.keys())
            return components
        except Exception as e:
            raise Exception('Getting components failed!, ', e)

    def config_thermodb_rule(self, config_file, name="ALL", disp=False) -> bool:
        '''
        Configs thermodb rule defined for each component

        Parameters
        ----------
        config_file: str
            config file path
        name: str
            name of the record, optional, default value is ALL.
        disp: bool
            display the config log

        Returns
        -------
        True : bool
            success

        Notes
        -----
        config_file is a yml file format as:
        ```
        EtOH:
            Pc: ['GENERAL','Pc']
            Tc: ['GENERAL','Tc']
            AcFa: ['GENERAL','AcFa']
            VaPr: ['VAPOR-PRESSURE','VaPr']
        MeOH:
            Pc: ['GENERAL','Pc']
            Tc: ['GENERAL','Tc']
            AcFa: ['GENERAL','AcFa']
            VaPr: ['VAPOR-PRESSURE','VaPr']
        ```
        '''
        try:
            # check
            if config_file:
                # check file
                if not os.path.exists(config_file):
                    raise Exception('Configuration file not found!')

                # set name
                name = str(name).strip()
                # load
                with open(config_file, 'r') as f:
                    _ref = yaml.load(f, Loader=yaml.FullLoader)

                    # check
                    if name == "ALL":
                        # check name exists
                        if _ref.keys():
                            # looping through
                            for key in _ref.keys():
                                # get record
                                record_thermodb_rule = _ref[key]

                                # check key exists
                                if key in self._thermodb.keys():
                                    # add
                                    self._thermodb_rule[key].update(
                                        record_thermodb_rule)

                                    # check disp
                                    if disp:
                                        print(
                                            f'{key} thermodb rule successfully registered.')
                                else:
                                    print(
                                        f'{key} not found, no thermodb provided!')
                            # res
                            return True
                        else:
                            raise Exception('Record not found!')
                    else:
                        # check name exists
                        if name in _ref.keys():
                            # get record
                            record_thermodb_rule = _ref[name]

                            # check name exists
                            if name in self._thermodb.keys():
                                # looping through
                                self._thermodb_rule[name].update(
                                    record_thermodb_rule)

                                # check disp
                                if disp:
                                    print(
                                        f'{name} thermodb rule successfully registered.')
                                # res
                                return True
                            else:
                                print(
                                    f'{name} not found, no thermodb provided!')
                                # res
                                return False
                        else:
                            print(f'{name} not found, no thermodb provided!')
                            return False

        except Exception as e:
            raise Exception('Configuration failed!, ', e)

    def add_thermodb_rule(self, rules):
        '''
        Adds a thermodb rule dict

        Parameters
        ----------
        rules: dict
            thermodb rule dict for all components

        Returns
        -------
        True : bool
            success

        Notes
        -----
        - A dictionary file with the following format:

        {
            'CO2':
                'Pc': ['GENERAL','Pc']
                'Tc': ['GENERAL','Tc']
                'AcFa': ['GENERAL','AcFa']
                'VaPr': ['VAPOR-PRESSURE','VaPr'],
        }
        '''
        try:
            for key, value in rules.items():
                # check key exist
                if key not in self._thermodb.keys():
                    # log warning
                    print(f"{key} is not in thermodb!")
                    continue

                # add
                self._thermodb_rule[key] = value
                # res
                return True
            # res
            return True
        except Exception as e:
            raise Exception('Adding new rule failed!, ', e)

    def delete_thermodb_rule(self, name):
        '''
        Deletes the current thermodb rule

        Parameters
        ----------
        name: str
            name of the record

        Returns
        -------
        True : bool
            success
        '''
        try:
            # check key exist
            if name not in self._thermodb_rule.keys():
                # log warning
                print(f"{name} is not in thermodb_rule!")
                return False

            # del
            del self._thermodb_rule[name]
            # res
            return True
        except Exception as e:
            raise Exception('Deleting rule failed!, ', e)

    def add_thermodb(self, name, data: pyThermoDB.docs.compbuilder.CompBuilder) -> bool:
        '''
        Adds new thermodb such as: CO2_thermodb

        Parameters
        ----------
        name: str
            name of the record
        data: pyThermoDB.docs.compbuilder.CompBuilder
            data of the record

        Returns
        -------
        True : bool
            success
        '''
        try:
            self._thermodb[name] = data
            # create thermodb rule
            self._thermodb_rule[name] = {}
            # res
            return True
        except Exception as e:
            raise Exception('Adding new record failed!, ', e)

    def update_thermodb(self, name, data: pyThermoDB.docs.compbuilder.CompBuilder) -> bool:
        '''
        Updates existing record

        Parameters
        ----------
        name: str
            name of the record
        data: pyThermoDB.docs.compbuilder.CompBuilder
            data of the record

        Returns
        -------
        True : bool
            success
        '''
        try:
            self._thermodb[name] = data
            # res
            return True
        except Exception as e:
            raise Exception('Updating record failed!, ', e)

    def delete_thermodb(self, name: str) -> bool:
        '''
        Deletes existing record

        Parameters
        ----------
        name: str
            name of the record

        Returns
        -------
        True : bool
            success
        '''
        try:
            del self._thermodb[name]
            # delete thermodb rule
            del self._thermodb_rule[name]
            # res
            return True
        except Exception as e:
            raise Exception('Deleting record failed!, ', e)

    def info_thermodb(self, name) -> dict:
        '''
        Gets info of thermodb

        Parameters
        ----------
        name: str
            name of the record

        Returns
        -------
        res : CompBuilder
            thermodb check
        '''
        try:
            # check key exist
            if name not in self._thermodb.keys():
                # log warning
                print(f"{name} is not in thermodb!")
                return None

            # res
            res = self._thermodb[name].check()
            return res
        except Exception as e:
            raise Exception('Getting info of record failed!, ', e)

    def build(self):
        '''
        Builds a datasource

        Parameters
        ----------
        None

        Returns
        -------
        datasource : dict
            datasource
        equationsource : dict
            equationsource

        Notes
        -----
        - A dictionary contains data and equations
        '''
        try:
            # components
            components = list(self._thermodb.keys())
            # datasource
            datasource = self._set_datasource(
                self._thermodb, self._thermodb_rule, components)
            # equationsource
            equationsource = self._set_equationsource(
                self._thermodb, self._thermodb_rule, components)

            # reset
            self._hub = {}
            # update hub

            # for each component
            for component in components:
                _data = datasource[component]
                _eq = equationsource[component]
                # save
                self._hub[component] = {**_data, **_eq}
            # res
            return datasource, equationsource
        except Exception as e:
            raise Exception('Building data/equation source failed!, ', e)

    def check(self):
        '''
        Checks data/equation source

        Parameters
        ----------
        None

        Returns
        -------
        thermodb : dict
            thermodb
        '''
        try:
            return self._hub
        except Exception as e:
            raise Exception('Checking data/equation source failed!, ', e)
