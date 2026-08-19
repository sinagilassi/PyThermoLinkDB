# import libs
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional, Literal

# SECTION: Thermo source item


class SourceConfig(BaseModel):
    source: Optional[Literal["model_source", "custom_source"]] = Field(
        default='model_source',
        description="Source type used when the source mode can be inferred.",
    )
    equation_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default=None,
        description="Source type: 'model_source' or 'custom_source'",
    )
    property_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default=None,
        description="Source type: 'model_source' or 'custom_source'",
    )
    constants_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default=None,
        description="Source type: 'model_source' or 'custom_source'",
    )
    matrix_data_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default=None,
        description="Source type: 'model_source' or 'custom_source'",
    )


# NOTE: thermo source hub config
ThermoSourceHubConfig = Dict[str, SourceConfig]
