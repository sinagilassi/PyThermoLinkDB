# import libs
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional


# NOTE: constants model
class CustomConstant(BaseModel):
    """
    Custom constant model for input validation.

    Attributes
    ----------
    name : str | None
        Name of the constant, e.g., 'enthalpy', 'entropy', 'Universal gas constant'.
    description : str | None
        Description of the constant, e.g., 'Enthalpy of formation at 298 K'.
    value : Any
        Value of the constant, e.g., 'enthalpy', 'entropy'.
    unit : str
        Unit of the constant, e.g., 'J/mol.K', 'kJ/mol'.
    symbol : str
        Symbol of the constant, e.g., 'H' for enthalpy, 'S' for entropy.
    """
    name: str | None = Field(
        default=None,
        description="Name of the constant, e.g., 'enthalpy', 'entropy'"
    )
    description: str | None = Field(
        default=None,
        description="Description of the constant, e.g., 'Enthalpy of formation at 298 K'"
    )
    value: Any = Field(
        ...,
        description="Value of the constant, e.g., 'enthalpy', 'entropy'"
    )
    unit: str | None = Field(
        ...,
        description="Unit of the constant, e.g., 'J/mol.K', 'kJ/mol'"
    )
    symbol: str = Field(
        ...,
        description="Symbol of the constant, e.g., 'H' for enthalpy, 'S' for entropy"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
