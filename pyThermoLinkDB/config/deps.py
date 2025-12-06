# import libs
from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class AppConfig:
    # ! whether to keep original label
    original_equation_label: bool = True


# this is like get_settings() in FastAPI
_current_config: AppConfig | None = None


def set_config(cfg: AppConfig) -> None:
    global _current_config
    _current_config = cfg


def get_config() -> AppConfig:
    if _current_config is None:
        # default config if not set
        return AppConfig()
    return _current_config
