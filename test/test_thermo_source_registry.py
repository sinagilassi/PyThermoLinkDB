from types import SimpleNamespace

from pythermodb_settings.models import Component

from pyThermoLinkDB.builders import ThermoSourceHub, ThermoSourceRegistry
from pyThermoLinkDB.builders.thermo_source_extractor import ThermoSourceExtractor
from pyThermoLinkDB.models import SourceConfig
from pyThermoLinkDB.utils.hub_tools import (
    thermo_source_hub_config_from_json,
    thermo_source_hub_config_from_yaml,
)


class FakeThermoSourceHub:
    def __init__(self):
        self.data = {"model_source": {"Tc": {"c1": "tc-src"}}}
        self.equations = {"model_source": {"Cp_IG": {"c1": "cp-eq"}}}
        self.constants = {"model_source": {"R": 8.314}}
        self.constant_sources = {"model_source": {"R": "r-src"}}

    def has_mode(self, source_type, symbol, mode):
        if mode == "data":
            return symbol in self.data.get(source_type, {})
        if mode == "equation":
            return symbol in self.equations.get(source_type, {})
        if mode == "constants":
            return symbol in self.constants.get(source_type, {})
        return False

    def get_comp_src(self, source_type, symbol, components=None):
        return self.data[source_type][symbol]

    def get_comp_eq(self, source_type, symbol, components=None):
        return self.equations[source_type][symbol]

    def get_const(self, source_type, symbol):
        return self.constants[source_type][symbol]

    def get_const_src(self, source_type, symbol):
        return self.constant_sources[source_type][symbol]


def make_mixture_hub():
    methanol = Component(name="methanol", formula="CH3OH", state="l")
    ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
    model = SimpleNamespace(thermo_src={
        "alpha": {
            "src": {
                "ethanol|methanol": "name-source",
                "C2H5OH|CH3OH": "formula-source",
            },
            "value": None,
            "mode": ["matrix_data"],
        },
    })
    hub = ThermoSourceHub(
        components=[methanol, ethanol],
        component_key="Formula-State",
        thermo_model_source=model,
        thermo_custom_source=None,
        mixtures=[[methanol, ethanol]],
        mixture_key="Formula",
    )
    return hub, methanol, ethanol


def test_thermo_source_registry_extracts_configured_modes_only():
    registry = ThermoSourceRegistry(
        thermo_src=FakeThermoSourceHub(),
        thermo_source_hub_config={
            "Tc": SourceConfig(),
            "Cp_IG": SourceConfig(),
            "R": SourceConfig(),
        },
    )

    assert registry.extract_sources() == {
        "Tc": {"src": {"c1": "tc-src"}},
        "Cp_IG": {"eq": {"c1": "cp-eq"}},
        "R": {"src": "r-src"},
    }


def test_thermo_source_registry_can_include_missing_fields():
    registry = ThermoSourceRegistry(
        thermo_src=FakeThermoSourceHub(),
        thermo_source_hub_config={"Tc": SourceConfig()},
    )

    assert registry.extract_sources(include_missing=True) == {
        "Tc": {
            "src": {"c1": "tc-src"},
            "eq": None,
        }
    }


def test_thermo_source_hub_registers_configured_sources():
    hub = ThermoSourceHub(
        components=[],
        component_key="Formula-State",
        thermo_model_source=None,
        thermo_custom_source=None,
    )
    hub._thermo_source = {
        "model_source": {
            "Tc": {
                "src": {"c1": "tc-src"},
                "eq": None,
                "value": None,
                "mode": ["data"],
            },
            "Cp_IG": {
                "src": None,
                "eq": {"c1": "cp-eq"},
                "value": None,
                "mode": ["equation"],
            },
            "R": {
                "src": "r-src",
                "eq": None,
                "value": 8.314,
                "mode": ["constants"],
            },
        },
        "custom_source": {},
    }
    hub.thermo_source_extractor = ThermoSourceExtractor(
        thermo_source=hub.thermo_source,
        component_key="Formula-State",
    )

    registered_source = hub.register_thermo_source(
        thermo_source_hub_config={
            "Tc": SourceConfig(),
            "Cp_IG": SourceConfig(),
            "R": SourceConfig(),
        },
    )

    assert registered_source == {
        "Tc": {"src": {"c1": "tc-src"}},
        "Cp_IG": {"eq": {"c1": "cp-eq"}},
        "R": {"src": "r-src"},
    }
    assert hub.thermo_source_registry.registry == registered_source


def test_thermo_source_hub_registers_configured_sources_from_string():
    hub = ThermoSourceHub(
        components=[],
        component_key="Formula-State",
        thermo_model_source=None,
        thermo_custom_source=None,
    )
    hub._thermo_source = {
        "model_source": {
            "Tc": {
                "src": {"c1": "tc-src"},
                "eq": None,
                "value": None,
                "mode": ["data"],
            },
        },
        "custom_source": {},
    }
    hub.thermo_source_extractor = ThermoSourceExtractor(
        thermo_source=hub.thermo_source,
        component_key="Formula-State",
    )

    registered_source = hub.register_thermo_source(
        thermo_source_hub_config="""
Tc:
  property_source: model_source
  equation_source:
  constants_source:
""",
    )

    assert registered_source == {"Tc": {"src": {"c1": "tc-src"}}}


def test_thermo_source_hub_config_from_json_builds_source_config_models():
    config = thermo_source_hub_config_from_json(
        '{"Tc": {"property_source": "custom_source", "equation_source": null}}'
    )

    assert config == {
        "Tc": SourceConfig(
            property_source="custom_source",
            equation_source=None,
        )
    }


def test_thermo_source_hub_config_from_yaml_builds_source_config_models():
    config = thermo_source_hub_config_from_yaml(
        """
Tc:
  property_source: custom_source
  equation_source:
R:
"""
    )

    assert config == {
        "Tc": SourceConfig(
            property_source="custom_source",
            equation_source=None,
        ),
        "R": SourceConfig(),
    }


def test_thermo_source_hub_config_from_yaml_accepts_source_type_shorthand():
    config = thermo_source_hub_config_from_yaml("Tc: model_source\n")

    assert config == {
        "Tc": SourceConfig(
            property_source="model_source",
            equation_source="model_source",
            constants_source="model_source",
            matrix_data_source="model_source",
        )
    }


def test_thermo_source_registry_uses_hub_mixture_key_for_registration():
    hub, methanol, ethanol = make_mixture_hub()

    registered_source = hub.register_thermo_source(
        thermo_source_hub_config={
            "alpha": SourceConfig(
                property_source=None,
                equation_source=None,
                constants_source=None,
                matrix_data_source="model_source",
            ),
        },
        mixtures=[[methanol, ethanol]],
    )

    assert registered_source == {
        "alpha": {"src": {"C2H5OH|CH3OH": "formula-source"}},
    }


def test_thermo_source_registry_uses_components_as_single_mixture():
    hub, methanol, ethanol = make_mixture_hub()

    registered_source = hub.register_thermo_source(
        thermo_source_hub_config={
            "alpha": SourceConfig(
                property_source=None,
                equation_source=None,
                constants_source=None,
                matrix_data_source="model_source",
            ),
        },
        components=[methanol, ethanol],
    )

    assert registered_source == {
        "alpha": {"src": {"C2H5OH|CH3OH": "formula-source"}},
    }
