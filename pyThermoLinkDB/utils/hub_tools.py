"""Helpers for source-hub configuration parsing."""

from __future__ import annotations

import json
from typing import Any, Mapping

import yaml

from ..models import SourceConfig, ThermoSourceHubConfig

_SOURCE_TYPES = ("model_source", "custom_source")


def thermo_source_hub_config_from_json(config: str) -> ThermoSourceHubConfig:
    """Convert JSON string content to a ``ThermoSourceHubConfig``."""
    return _thermo_source_hub_config_from_mapping(json.loads(config))


def thermo_source_hub_config_from_yaml(config: str) -> ThermoSourceHubConfig:
    """Convert YAML string content to a ``ThermoSourceHubConfig``."""
    data = yaml.safe_load(config)
    return _thermo_source_hub_config_from_mapping(data)


def thermo_source_hub_config_from_str(config: str) -> ThermoSourceHubConfig:
    """Convert JSON or YAML string content to a ``ThermoSourceHubConfig``."""
    try:
        return thermo_source_hub_config_from_json(config)
    except json.JSONDecodeError:
        return thermo_source_hub_config_from_yaml(config)


def ensure_thermo_source_hub_config(
        config: ThermoSourceHubConfig | str,
) -> ThermoSourceHubConfig:
    """Return ``config`` as a ``ThermoSourceHubConfig``."""
    if isinstance(config, str):
        return thermo_source_hub_config_from_str(config)
    return _thermo_source_hub_config_from_mapping(config)


def _thermo_source_hub_config_from_mapping(
        config: Any,
) -> ThermoSourceHubConfig:
    if not isinstance(config, Mapping):
        raise TypeError("Thermo source hub config must be a mapping.")

    return {
        str(symbol): _source_config_from_value(source_config)
        for symbol, source_config in config.items()
    }


def _source_config_from_value(source_config: Any) -> SourceConfig:
    if isinstance(source_config, SourceConfig):
        return source_config
    if source_config is None:
        return SourceConfig()
    if isinstance(source_config, str):
        if source_config not in _SOURCE_TYPES:
            raise ValueError(
                "Source config shorthand must be 'model_source' or "
                "'custom_source'."
            )
        source_type = source_config
        return SourceConfig(
            property_source=source_type,
            equation_source=source_type,
            constants_source=source_type,
            matrix_data_source=source_type,
        )
    return SourceConfig(**source_config)
