# import libs
import logging
from typing import Dict, Optional
from pyThermoDB.core import TableEquation
# locals
from ..models.source import DataSymbol, EquationSymbol, EqSym


# NOTE: logger
logger = logging.getLogger(__name__)


class ThermoUtils:

    def __init__(self):
        pass

    # SECTION: data symbol extraction
    def extract_data_symbols(
            self,
            datasource: Dict
    ) -> Optional[Dict[str, DataSymbol]]:
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
            # NOTE: validation
            if (
                not datasource or
                len(datasource) == 0
            ):
                logger.warning(
                    "No data source provided for extracting symbols.")
                return None

            # NOTE: extract symbols
            data_symbols = {}
            for comp, prop_dict in datasource.items():
                data_symbols[comp] = {}
                for prop, value in prop_dict.items():
                    if isinstance(value, dict) and 'symbol' in value:
                        data_symbols[comp][prop] = {
                            'name': value.get('name', None) or value.get('property_name', None) or 'not found',
                            'symbol': value['symbol'],
                            'unit': value.get('unit', '-')
                        }

            # >> check
            if not data_symbols or len(data_symbols) == 0:
                logger.warning("No data symbols found in the data source.")
                return None

            # res
            return data_symbols
        except Exception as e:
            raise Exception(f"Error in extracting data symbols: {e}") from e

    # SECTION: equation symbol extraction
    def extract_equation_symbols(
            self,
            equationsource: Dict
    ) -> Optional[Dict[str, EquationSymbol]]:
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
            # NOTE: validation
            if (
                not equationsource or
                len(equationsource) == 0
            ):
                logger.warning(
                    "No equation source provided for extracting symbols.")
                return None

            # NOTE: extract symbols
            equation_symbols = {}
            for comp, eq_dict in equationsource.items():
                equation_symbols[comp] = {}
                for eq_name, eq in eq_dict.items():

                    # >> check eq type
                    if isinstance(eq, TableEquation):
                        # get return
                        rets = eq.eq_return()
                        # get arguments
                        args = eq.eq_args()
                        # get return symbol
                        ret_symbol = eq.get_return_symbols()
                        # get argument symbols
                        arg_symbols = eq.get_arg_symbols()

                        # store
                        equation_symbols[comp][eq_name] = EqSym(
                            arg_symbols=arg_symbols,
                            ret_symbols=ret_symbol,
                            args=args,
                            rets=rets,
                        )

            # >> check
            if (
                not equation_symbols or
                len(equation_symbols) == 0
            ):
                logger.warning(
                    "No equation symbols found in the equation source.")
                return None

            # res
            return equation_symbols
        except Exception as e:
            raise Exception(
                f"Error in extracting equation symbols: {e}"
            ) from e

    def extract_constants_symbols(
            self,
            constants_source: Dict
    ) -> Optional[Dict[str, DataSymbol]]:
        '''
        Extract constants symbols from the constants source.

        Parameters
        ----------
        constants_source : dict
            The constants source dictionary.

        Returns
        -------
        constants_symbols : Optional[Dict[str, DataSymbol]]
            The extracted constants symbols.
        '''
        try:
            # NOTE: validation
            if (
                not constants_source or
                len(constants_source) == 0
            ):
                logger.warning(
                    "No constants source provided for extracting symbols.")
                return None

            # NOTE: extract symbols
            constants_symbols = {}
            for const_name, const_info in constants_source.items():
                # >> check const info type
                if (
                    isinstance(const_info, dict) and
                    'symbol' in const_info
                ):
                    # set
                    constants_symbols[const_name] = {
                        'name': const_info.get('name', None) or const_info.get('constant_name', None) or 'not found',
                        'symbol': const_info['symbol'],
                        'unit': const_info.get('unit', '-')
                    }

            # >> check
            if (
                not constants_symbols or
                len(constants_symbols) == 0
            ):
                logger.warning(
                    "No constants symbols found in the constants source.")
                return None

            # res
            return constants_symbols
        except Exception as e:
            raise Exception(
                f"Error in extracting constants symbols: {e}"
            ) from e
