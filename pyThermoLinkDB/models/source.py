# import libs
from pydantic import BaseModel
from typing import Dict, Any
from pyThermoDB import TableData, TableEquation, TableMatrixData, TableMatrixEquation
from pyThermoDB.models import Component
# local


# NOTE: data source
DataSource = Dict[str, Any]
# NOTE: equation source
EquationSource = Dict[str, TableEquation | TableMatrixEquation]


class ComponentModelSource(BaseModel):
    '''
    Component model source containing data source and equation source

    Attributes
    ----------
    data_source: Dict[str, Any]
        Data source dictionary
    equation_source: Dict[str, Any]
        Equation source dictionary
    check_labels: bool
        Whether to check labels in the component thermodb based on the provided rules
    label_link: bool
        Whether all labels in the rules are found in the component thermodb
    '''
    component: Component
    data_source: Dict[str, DataSource]
    equation_source: Dict[str, EquationSource]
    check_labels: bool = True
    label_link: bool = True

    class Config:
        arbitrary_types_allowed = True


ComponentThermoDBRules = Dict[str, Dict[str, str]]


class ModelSource(BaseModel):
    '''
    Model source containing data source and equation source for multiple components

    Attributes
    ----------
    data_source: Dict[str, Dict[str, DataSource]]
        Data source dictionary for multiple components
    equation_source: Dict[str, Dict[str, EquationSource]]
        Equation source dictionary for multiple components
    all_check_labels: Dict[str, bool]
        Dictionary indicating whether labels were checked for each component
    all_label_link: Dict[str, bool]
        Dictionary indicating whether all labels in the rules were found for each component
    '''
    data_source: Dict[str, Dict[str, DataSource]]
    equation_source: Dict[str, Dict[str, EquationSource]]
    all_check_labels: Dict[str, bool]
    all_label_link: Dict[str, bool]

    class Config:
        arbitrary_types_allowed = True
