# import libs
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional, Literal

# SECTION: Thermo source item


class SourceConfig(BaseModel):
    equation_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default='model_source',
        description="Source type: 'model_source' or 'custom_source'",
    )
    property_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default='model_source',
        description="Source type: 'model_source' or 'custom_source'",
    )
    constants_source: Optional[Literal["model_source", "custom_source"]] = Field(
        default='model_source',
        description="Source type: 'model_source' or 'custom_source'",
    )


# NOTE: thermo source hub config
ThermoSourceHubConfig = Dict[str, SourceConfig]
