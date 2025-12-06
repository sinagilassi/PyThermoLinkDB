# import libs
from typing import Any, Dict, List, Callable
from pydantic import BaseModel, Field, ConfigDict
from pyThermoDB.core import TableEquation
from pyThermoDB.models import EquationResult

# NOTE: Component Equation Source


class ComponentEquationSource(BaseModel):
    '''
    Equation Builder Result Model

    Attributes
    ----------
    source: TableEquation
        The equation source from PyThermoDB
    num: int
        The equation number
    body: str
        The equation body
    args: Dict[str, Any]
        The equation arguments
    arg_symbols: Dict[str, Any]
        The equation argument symbols
    args_identifiers: List[str]
        The equation argument identifiers
    returns: Dict[str, Any]
        The equation returns
    return_symbols: Dict[str, Any]
        The equation return symbols
    return_identifiers: List[str]
        The equation return identifiers
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    source: TableEquation = Field(
        ...,
        description="The equation value."
    )
    inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="The equation inputs."
    )
    num: int = Field(
        ...,
        description="The equation number."
    )
    fn: Callable[..., EquationResult] = Field(
        ...,
        description="The equation function."
    )
    body: str = Field(
        ...,
        description="The equation body."
    )
    args: Dict[str, Any] = Field(
        default_factory=dict,
        description="The equation arguments."
    )
    arg_symbols: Dict[str, Any] = Field(
        default_factory=dict,
        description="The equation argument symbols."
    )
    arg_identifiers: List[str] = Field(
        default_factory=list,
        description="The equation argument identifiers."
    )
    returns: Dict[str, Any] = Field(
        default_factory=dict,
        description="The equation returns."
    )
    return_symbols: Dict[str, Any] = Field(
        default_factory=dict,
        description="The equation return symbols."
    )
    return_identifiers: List[str] = Field(
        default_factory=list,
        description="The equation return identifiers."
    )


class CalcResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: float = Field(
        ...,
        description="Calculated value"
    )
    unit: str = Field(
        ...,
        description="Unit of the calculated value"
    )
    symbol: str = Field(
        ...,
        description="Symbol representing the calculated property"
    )


class PropResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: float | int = Field(
        ...,
        description="Property value"
    )
    unit: str = Field(
        ...,
        description="Unit of the property value"
    )
    symbol: str = Field(
        ...,
        description="Symbol representing the property"
    )
