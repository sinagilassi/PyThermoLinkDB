"""Helpers for source-hub configuration parsing."""

from __future__ import annotations

import json
from typing import Any, Mapping

import yaml

from ..models import (
    CustomSourceConfig,
    ModelSourceConfig,
    SourceConfig,
    ThermoSourceHubConfig,
)

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
    return _thermo_source_hub_config_from_mapping(_load_json_or_yaml(config))


def ensure_thermo_source_hub_config(
        config: ThermoSourceHubConfig | str,
) -> ThermoSourceHubConfig:
    """Return ``config`` as a ``ThermoSourceHubConfig``."""
    if isinstance(config, str):
        return thermo_source_hub_config_from_str(config)
    return _thermo_source_hub_config_from_mapping(config)


def model_source_config_from_json(config: str) -> ModelSourceConfig:
    """Convert JSON string content to a ``ModelSourceConfig``."""
    return _model_source_config_from_mapping(json.loads(config))


def model_source_config_from_yaml(config: str) -> ModelSourceConfig:
    """Convert YAML string content to a ``ModelSourceConfig``."""
    return _model_source_config_from_mapping(yaml.safe_load(config))


def model_source_config_from_str(config: str) -> ModelSourceConfig:
    """Convert JSON or YAML string content to a ``ModelSourceConfig``."""
    return _model_source_config_from_mapping(_load_json_or_yaml(config))


def ensure_model_source_config(
        config: ModelSourceConfig | str | None,
) -> ModelSourceConfig | None:
    """Return ``config`` as a ``ModelSourceConfig`` when provided."""
    if config is None:
        return None
    if isinstance(config, str):
        return model_source_config_from_str(config)
    return _model_source_config_from_mapping(config)


def custom_source_config_from_json(config: str) -> CustomSourceConfig:
    """Convert JSON string content to a ``CustomSourceConfig``."""
    return _custom_source_config_from_mapping(json.loads(config))


def custom_source_config_from_yaml(config: str) -> CustomSourceConfig:
    """Convert YAML string content to a ``CustomSourceConfig``."""
    return _custom_source_config_from_mapping(yaml.safe_load(config))


def custom_source_config_from_str(config: str) -> CustomSourceConfig:
    """Convert JSON or YAML string content to a ``CustomSourceConfig``."""
    return _custom_source_config_from_mapping(_load_json_or_yaml(config))


def ensure_custom_source_config(
        config: CustomSourceConfig | str | None,
) -> CustomSourceConfig | None:
    """Return ``config`` as a ``CustomSourceConfig`` when provided."""
    if config is None:
        return None
    if isinstance(config, str):
        return custom_source_config_from_str(config)
    return _custom_source_config_from_mapping(config)


def _load_json_or_yaml(config: str) -> Any:
    try:
        return json.loads(config)
    except json.JSONDecodeError:
        return yaml.safe_load(config)


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
        return SourceConfig(source=source_type)
    return SourceConfig(**source_config)


def _model_source_config_from_mapping(config: Any) -> ModelSourceConfig:
    if isinstance(config, ModelSourceConfig):
        return config
    if config is None:
        return ModelSourceConfig()
    if not isinstance(config, Mapping):
        raise TypeError("Model source config must be a mapping.")
    return ModelSourceConfig(**config)


def _custom_source_config_from_mapping(config: Any) -> CustomSourceConfig:
    if isinstance(config, CustomSourceConfig):
        return config
    if config is None:
        return CustomSourceConfig()
    if not isinstance(config, Mapping):
        raise TypeError("Custom source config must be a mapping.")
    return CustomSourceConfig(**config)
