# import libs
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
from pyThermoDB import (
    TableData,
    TableEquation,
    TableMatrixData,
    TableMatrixEquation
)
from pythermodb_settings.models import Component
# local


# NOTE: data source
PropertyData = Dict[str, str | float | int | bool | None]
DataSource = Dict[str, PropertyData]
# NOTE: equation source
EquationSource = Dict[str, TableEquation | TableMatrixEquation]


# NOTE: component model source
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
    component: Component
    data_source: Dict[str, DataSource]
    equation_source: Dict[str, EquationSource]
    check_labels: Optional[bool] = None
    label_link: Optional[bool] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )


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
    components: list[Component]
    data_source: Dict[str, DataSource]
    equation_source: Dict[str, EquationSource]
    check_labels: Optional[bool] = None
    label_link: Optional[bool] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )


# NOTE: model source
class ModelSource(BaseModel):
    '''
    Model source containing data source and equation source for multiple components

    Attributes
    ----------
    data_source: Dict[str, Dict[str, DataSource]]
        Data source dictionary for multiple components
    equation_source: Dict[str, Dict[str, EquationSource]]
        Equation source dictionary for multiple components
    '''
    data_source: Dict[str, DataSource]
    equation_source: Dict[str, EquationSource]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
