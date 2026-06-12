# import libs
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional, List, Any
from pyThermoDB import (
    TableEquation,
    TableMatrixData,
    TableMatrixEquation,
    TableConstants
)
from pythermodb_settings.models import Component
# local


# NOTE: data source
PropertyData = Dict[str, str | float | int | bool | None]
DataSource = Dict[str, PropertyData | TableMatrixData]
# ?? defines as:
#   'Tc': {
#     'property_name': 'critical-temperature',
#     'symbol': 'Tc',
#     'unit': 'K',
#     'value': '513.9',
#     'message': 'No message',
#     'databook_name': 'CUSTOM-REF-1',
#     'table_name': 'general-data'
# }

# NOTE: equation source
EquationSource = Dict[str, TableEquation | TableMatrixEquation]
# ?? defines as:
#  {
#     'Cp_IG': <pyThermoDB.core.tableequation.TableEquation object at 0x000002105ED8C990>,
#     'VaPr': <pyThermoDB.core.tableequation.TableEquation object at 0x000002105E8359D0>,
#     'Cp_LIQ': <pyThermoDB.core.tableequation.TableEquation object at 0x000002105ED9D450>,
#     'EnVap': <pyThermoDB.core.tableequation.TableEquation object at 0x000002105ED2C110>
# }

# NOTE: constants source
ConstantsSource = Dict[str, Any]
# ?? defines as:
# 'R': 8.31446261815324
# 'dH_rxn': {
#     'reaction1': {
#         'value': -100.0,
#         'unit': 'kJ/mol',
#         },
#    'reaction2': {
#         'value': -200.0,
#         'unit': 'kJ/mol',
#         }
# }
# 'K_eq': [1.0, 2.0, 3.0]
# 'custom_constant': any value


# NOTE: symbol
# ?? data source symbol
DataSymbol = Dict[str, Dict[str, str]]
# ?? defines as:
data_symbol_example = {
    'CO2-g': {

    }
}


# NOTE: equation symbol model
class EqSym(BaseModel):
    arg_symbols: List[str]
    ret_symbols: List[str]
    args: Dict[str, Dict[str, str]]
    rets: Dict[str, Dict[str, str]]


EquationSymbol = Dict[str, EqSym]

# ?? constants source symbol
ConstantsSymbol = Dict[str, Dict[str, Any]]

# SECTION: component model source


class ComponentModelSource(BaseModel):
    '''
    Component model source containing data source and equation source

    Attributes
    ----------
    component: Component
        Component information
    data_source: Dict[str, DataSource]
        Data source dictionary
    equation_source: Dict[str, EquationSource]
        Equation source dictionary
    check_labels: bool
        Whether to check labels in the component thermodb based on the provided rules
    label_link: bool
        Whether all labels in the rules are found in the component thermodb
    '''
    component: Component = Field(
        ...,
        description="Component object containing component information such as name, formula, state, and composition"
    )
    data_source: Dict[str, DataSource] = Field(
        ...,
        description="Data source dictionary for the component"
    )
    equation_source: Dict[str, EquationSource] = Field(
        ...,
        description="Equation source dictionary for the component"
    )
    check_labels: Optional[bool] = None
    label_link: Optional[bool] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )


# SECTION: mixture model source
class MixtureModelSource(BaseModel):
    '''
    Mixture model source containing data source and equation source for multiple components

    Attributes
    ----------
    components: List[Component]
        List of components in the mixture
    data_source: Dict[str, DataSource]
        Data source dictionary for the mixture
    equation_source: Dict[str, EquationSource]
        Equation source dictionary for the mixture
    check_labels: bool
        Whether to check labels in the mixture thermodb based on the provided rules
    label_link: bool
        Whether all labels in the rules are found in the mixture thermodb
    '''
    components: list[Component] = Field(
        ...,
        description="List of components in the mixture"
    )
    data_source: Dict[str, DataSource] = Field(
        ...,
        description="Data source dictionary for the mixture"
    )
    equation_source: Dict[str, EquationSource] = Field(
        ...,
        description="Equation source dictionary for the mixture"
    )

    check_labels: Optional[bool] = None
    label_link: Optional[bool] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )

# SECTION: Constants model source


class ConstantsModelSource(BaseModel):
    '''
    Constants model source containing constants source

    Attributes
    ----------
    constants_source: Dict[str, TableConstants]
        Constants source dictionary for multiple components
    '''
    constants_source: ConstantsSource = Field(
        ...,
        description="Constants source dictionary for multiple components"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )


# SECTION: model source
class ModelSource(BaseModel):
    '''
    Model source containing data source and equation source for multiple components

    Attributes
    ----------
    data_source: Dict[str, Dict[str, DataSource]]
        Data source dictionary for multiple components
    equation_source: Dict[str, Dict[str, EquationSource]]
        Equation source dictionary for multiple components
    constants_source: Optional[Dict[str, TableConstants]]
        Optional constants source dictionary for multiple components
    data_symbols: Optional[Dict[str, Dict[str, DataSymbol]]] = None
        Optional data symbol dictionary for multiple components
    equation_symbols: Optional[Dict[str, Dict[str, EquationSymbol]]] = None
        Optional equation symbol dictionary for multiple components
    '''
    data_source: Dict[str, DataSource] = Field(
        ...,
        description="Data source dictionary for multiple components"
    )
    equation_source: Dict[str, EquationSource] = Field(
        ...,
        description="Equation source dictionary for multiple components"
    )
    constants_source: Optional[Dict[str, TableConstants]] = Field(
        default_factory=dict,
        description="Constants source dictionary for multiple components"
    )

    # optional
    data_symbols: Optional[Dict[str, DataSymbol]] = None
    equation_symbols: Optional[Dict[str, EquationSymbol]] = None
    constants_symbols: Optional[Dict[str, ConstantsSymbol]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
