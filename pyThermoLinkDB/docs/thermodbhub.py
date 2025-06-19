# import packages/modules
import os
from pathlib import Path
from typing import Optional, List
from pyThermoDB import CompBuilder
# local
from .thermolink import ThermoLink
from .utils import (
    generate_summary,
    thermodb_file_loader,
    thermodb_parser,
)


class ThermoDBHub(ThermoLink):
    """ThermoDBHub class used to manage thermodynamic databases."""
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

    def items(self):
        '''
        Gets all items in thermodb link

        Returns
        -------
        list
            list of items in thermodb link
        '''
        try:
            return list(self._thermodb.keys())
        except Exception as e:
            raise Exception('Getting components failed!, ', e)

    def config_thermodb_rule(self,
                             config_file: str | Path,
                             names: Optional[List[str]] = None,
                             disp: bool = False
                             ) -> bool | str:
        '''
        Configs thermodb rule defined for each component

        Parameters
        ----------
        config_file: str | Path
            config file path or content, file can be a `yml`, `md`, or `txt` file
            or a string content in the same format
        names: List[str]
            name of the record, optional, default is None
        disp: bool
            display the config log

        Returns
        -------
        log_info : list
            log info of the config

        Notes
        -----
        config_file is a `yml file` format as:

        ```yaml
        EtOH:
            DATA:
                Pc: Pc1
                Tc: Tc2
                AcFa: AcFa3
            EQUATIONS:
                VAPOR-PRESSURE: VaPr
        MeOH:
            DATA:
                Pc: Pc
                Tc: Tc
                AcFa: AcFa
            EQUATIONS:
                VAPOR-PRESSURE: VaPr
                HEAT-CAPACITY: Cp_IG
        ```
        '''
        try:
            # log info
            log_info = ['Logging thermodb rule...']

            # SECTION: check config_file
            if not config_file:
                # log warning
                _log = 'No configuration file provided!'
                if disp:
                    print(_log)
                log_info.append(_log)

                # set
                log_info = '\n'.join(log_info)
                # return
                return log_info

            # SECTION: check file
            # check the config_file is a file or content
            if isinstance(config_file, str):
                # check if config_file is a file
                if os.path.isfile(config_file):
                    # ! load thermodb file
                    _ref = thermodb_file_loader(config_file)
                else:
                    # ! parse thermodb content
                    _ref = thermodb_parser(config_file)
            elif isinstance(config_file, Path):
                # check if config_file is a file
                if config_file.is_file():
                    # ! load thermodb file
                    _ref = thermodb_file_loader(config_file)
                else:
                    # ! parse thermodb content
                    _ref = thermodb_parser(config_file.read_text())
            else:
                raise TypeError(
                    'config_file should be a string or a file path!')

            # SECTION: analyze the reference
            # NOTE: check if _ref is None
            if _ref is None:
                _log = 'thermodb rule file is empty!'
                # log warning
                if disp:
                    print(_log)
                log_info.append(_log)

                # set
                log_info = '\n'.join(log_info)
                # return
                return log_info

            # NOTE: check config mode
            if names is None:
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
                            _log = f'{key} thermodb rule successfully set.'
                            if disp:
                                print(_log)
                            log_info.append(_log)
                        else:
                            _log = f'{key} not found, no thermodb provided!'
                            # log warning
                            if disp:
                                print(_log)
                            log_info.append(_log)
                else:
                    # empty thermodb rule
                    _log = 'No thermodb rule found!'
                    # log warning
                    if disp:
                        print(_log)
                    log_info.append(_log)

                    # set
                    log_info = '\n'.join(log_info)

                    # return
                    return log_info
            else:
                # SECTION
                # check keys
                if not _ref.keys():
                    _log = 'No thermodb rule found!'
                    # log warning
                    if disp:
                        print(_log)
                    log_info.append(_log)

                    # set
                    log_info = '\n'.join(log_info)
                    # return
                    return log_info

                # looping through names
                for name in names:
                    # NOTE: check name exists
                    if name in _ref.keys():
                        # get record
                        record_thermodb_rule = _ref[name]

                        # check name exists
                        if name in self._thermodb.keys():
                            # looping through
                            self._thermodb_rule[name].update(
                                record_thermodb_rule)

                            # check disp
                            _log = f'{name} thermodb rule successfully registered.'
                            if disp:
                                print(_log)
                            log_info.append(_log)
                        else:
                            _log = f'{name} not found, no thermodb provided!'
                            if disp:
                                print(_log)
                            log_info.append(_log)
                    else:
                        _log = f'{name} not found, no thermodb provided!'
                        if disp:
                            print(_log)
                        log_info.append(_log)

            # NOTE: convert log_info to string
            if isinstance(log_info, list):
                log_info = '\n'.join(log_info)

            return log_info

        except Exception as e:
            raise Exception('Configuration failed!, ', e)

    def add_thermodb_rule(self,
                          item: str,
                          rules: dict
                          ) -> bool | str:
        '''
        Adds or update a thermodb rule for a thermodb rule item.

        Parameters
        ----------
        item: str
            name of the record
        rules: dict
            thermodb rule dict for all components

        Returns
        -------
        bool
            True if success, False otherwise

        Notes
        -----
        - A dictionary file with the following format:

        ```python
        # example of thermodb rule
        thermodb_rule_CO2 = {
            'DATA': {
                'Pc': 'Pc1',
                'Tc': 'Tc1',
                'AcFa': 'AcFa1'
            },
            'EQUATIONS': {
                'vapor-pressure': 'VaPr1',
                'heat-capacity': 'Cp_IG1'
            }
        }

        # add thermodb rule for CO2
        thub1.add_thermodb_rule('CO2', thermodb_rule_CO2)
        ```
        '''
        try:
            # logger
            log_info = ['Logging thermodb rule...']

            # log res
            def log_res(x): return "\n".join(x)

            # NOTE: check item exists
            if item not in self._thermodb_rule.keys():
                # add item
                self._thermodb_rule[item] = {}
                # log
                log_ = f"{item} thermodb successfully set."
                # log warning
                log_info.append(log_)

            # NOTE: check rules
            if 'DATA' not in self._thermodb_rule[item].keys():
                # add DATA
                self._thermodb_rule[item]['DATA'] = {}

                # log
                log_ = f"{item} DATA successfully set."
                # log warning
                log_info.append(log_)

            if 'EQUATIONS' not in self._thermodb_rule[item].keys():
                # add EQUATIONS
                self._thermodb_rule[item]['EQUATIONS'] = {}

                # log
                log_ = f"{item} EQUATIONS successfully set."
                # log warning
                log_info.append(log_)

            # NOTE: check item exist
            if item not in self._thermodb_rule.keys():
                # log warning
                log_ = f"{item} is not in thermodb rule!"
                # log warning
                log_info.append(log_)

                # res
                return log_res(log_info)

            # NOTE: add DATA
            if 'DATA' in rules.keys():
                # data
                data_ = rules['DATA']
                # check data
                if not isinstance(data_, dict):
                    raise Exception('DATA should be a dictionary!')

                # check data exist
                if not data_.keys():
                    raise Exception('DATA is empty!')

                # looping through data
                for k, v in data_.items():
                    # initialize
                    if k not in self._thermodb_rule[item].keys():
                        # add data (new record)
                        self._thermodb_rule[item]['DATA'][k] = {}

                    # add data (update record)
                    self._thermodb_rule[item]['DATA'][k] = v

                    # log
                    log_ = f"{item} {k} successfully set."
                    # log warning
                    log_info.append(log_)

            # NOTE: add EQUATIONS
            if 'EQUATIONS' in rules.keys():
                # equations
                equations_ = rules['EQUATIONS']
                # check equations
                if not isinstance(equations_, dict):
                    raise Exception('EQUATIONS should be a dictionary!')

                # check equations exist
                if not equations_.keys():
                    raise Exception('EQUATIONS is empty!')

                # looping through equations
                for k, v in equations_.items():
                    # initialize
                    if k not in self._thermodb_rule[item].keys():
                        # add equations (new record)
                        self._thermodb_rule[item]['EQUATIONS'][k] = {}

                    # add equations (update record)
                    self._thermodb_rule[item]['EQUATIONS'][k] = v
                    # log
                    log_ = f"{item} {k} successfully set."
                    # log warning
                    log_info.append(log_)

            # NOTE: check if log_info is empty
            if len(log_info) == 1:
                # log warning
                log_ = f"No thermodb rule found!"
                # log warning
                log_info.append(log_)

            # res
            return log_res(log_info)

        except Exception as e:
            raise Exception('Adding new rule failed!, ', e)

    def delete_thermodb_rule(self,
                             name: str
                             ) -> bool:
        '''
        Deletes an item from thermodb rule

        Parameters
        ----------
        name: str
            name of the record to be deleted

        Returns
        -------
        bool
            True if success, False otherwise
        '''
        try:
            # check key exist
            if name not in self._thermodb_rule.keys():
                # log warning
                print(f"{name} is not in thermodb rule!")
                return False

            # del
            self._thermodb_rule[name] = {}
            # res
            return True
        except Exception as e:
            raise Exception('Deleting rule failed!, ', e)

    def add_thermodb(self,
                     name: str,
                     data: CompBuilder
                     ) -> bool:
        '''
        Adds new thermodb such as: CO2_thermodb

        Parameters
        ----------
        name: str
            name of the record
        data: CompBuilder
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

    def update_thermodb(self,
                        name,
                        data: CompBuilder
                        ) -> bool:
        '''
        Updates existing record

        Parameters
        ----------
        name: str
            name of the record
        data: pyThermoDB.CompBuilder
            data of the record

        Returns
        -------
        bool:
            True if success, False otherwise
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
        bool
            True if success, False otherwise
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
                # raise
                raise Exception(f"{name} is not in thermodb!")

            # res
            res = self._thermodb[name].check()
            return res
        except Exception as e:
            raise Exception('Getting info of record failed!, ', e)

    def build(self):
        '''
        Builds `datasource` and `equationsource` for each component registered in thermodb

        Parameters
        ----------
        None

        Returns
        -------
        datasource : dict
            datasource including component data such as Tc, Pc, etc.
        equationsource : dict
            equationsource including component equations such as VAPOR-PRESSURE, etc.

        Notes
        -----
        - A dictionary contains data and equations

        ```python
        # CO2 data
        dt1_ = datasource['CO2']['Pc']
        print(type(dt1_))
        print(dt1_)

        # MeOH data
        dt2_ = datasource['MeOH']['Tc']
        print(type(dt2_))
        print(dt2_)

        # NRTL data
        dt3_ = datasource['NRTL']['alpha_i_j']
        print(type(dt3_))
        print(dt3_.ij("Alpha_methanol_ethanol"))

        # CO2 equation
        eq1_ = equationsource['CO2']['VaPr']
        print(type(eq1_))
        print(eq1_)
        print(eq1_.args)
        print(eq1_.cal(T=298.15))

        # nrtl equation
        eq2_ = equationsource['NRTL']['tau_i_j']
        print(type(eq2_))
        print(eq2_)
        print(eq2_.args)
        print(eq2_.cal(T=298.15))
        ```
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
        hub : dict
            hub data
        '''
        try:
            # check summary
            return generate_summary(self._hub)
        except Exception as e:
            raise Exception('Checking data/equation source failed!, ', e)
