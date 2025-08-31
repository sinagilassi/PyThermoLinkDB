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
    '''
    component: Component
    data_source: Dict[str, DataSource]
    equation_source: Dict[str, EquationSource]

    class Config:
        arbitrary_types_allowed = True


ComponentThermoDBRules = Dict[str, Dict[str, str]]
