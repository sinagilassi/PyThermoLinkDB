# import libs
import logging
from typing import Dict, Optional
from pyThermoDB.core import TableEquation
# locals
from ..models.source import DataSymbol, EquationSymbol, EqSym


# NOTE: logger
logger = logging.getLogger(__name__)


class ThermoUtils:

    # SECTION: data symbol extraction
    @staticmethod
    def extract_data_symbols(datasource: Dict) -> Optional[Dict[str, DataSymbol]]:
        '''
        Extract data symbols from the data source.

        Parameters
        ----------
        datasource : dict
            The data source dictionary.

        Returns
        -------
        data_symbols : Optional[Dict[str, DataSymbol]]
            The extracted data symbols.
        '''
        try:
            # NOTE: extract symbols
            data_symbols = {}
            for comp, prop_dict in datasource.items():
                data_symbols[comp] = {}
                for prop, value in prop_dict.items():
                    if isinstance(value, dict) and 'symbol' in value:
                        data_symbols[comp][prop] = value['symbol']

            # >> check
            if not data_symbols or len(data_symbols) == 0:
                logger.warning("No data symbols found in the data source.")
                return None

            # res
            return data_symbols
        except Exception as e:
            raise Exception(f"Error in extracting data symbols: {e}") from e

    # SECTION: equation symbol extraction
    @staticmethod
    def extract_equation_symbols(equationsource: Dict) -> Optional[Dict[str, EquationSymbol]]:
        '''
        Extract equation symbols from the equation source.

        Parameters
        ----------
        equationsource : dict
            The equation source dictionary.

        Returns
        -------
        equation_symbols : Optional[Dict[str, EquationSymbol]]
            The extracted equation symbols.
        '''
        try:
            # NOTE: extract symbols
            equation_symbols = {}
            for comp, eq_dict in equationsource.items():
                equation_symbols[comp] = {}
                for eq_name, eq in eq_dict.items():

                    # >> check eq type
                    if isinstance(eq, TableEquation):
                        # get return symbol
                        ret_symbol = eq.get_return_symbols()
                        # get argument symbols
                        arg_symbols = eq.get_arg_symbols()

                        # store
                        equation_symbols[comp][eq_name] = EqSym(
                            args=arg_symbols,
                            rets=ret_symbol
                        )

            # >> check
            if not equation_symbols or len(equation_symbols) == 0:
                logger.warning(
                    "No equation symbols found in the equation source.")
                return None

            # res
            return equation_symbols
        except Exception as e:
            raise Exception(
                f"Error in extracting equation symbols: {e}") from e
