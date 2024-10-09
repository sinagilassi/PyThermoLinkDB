# THERMODB

# import packages/modules

# local
from .thermolink import ThermoLink


class ThermoDBHub(ThermoLink):
    # vars
    _thermodb = {}
    _thermodb_rule = {}

    def __init__(self):
        # init super class
        ThermoLink.__init__()

    @property
    def thermodb(self):
        return self._thermodb

    @property
    def thermodb_rule(self):
        return self._thermodb_rule

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

    def add_thermodb(self, name, data):
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
            # res
            return True
        except Exception as e:
            raise Exception('Adding new record failed!, ', e)

    def update_thermodb(self, name, data):
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

    def delete_thermodb(self, name):
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
        '''
        try:
            # res
            return self._build_datasource(self._thermodb, self._thermodb_rule)
        except Exception as e:
            raise Exception('Building datasource failed!, ', e)
