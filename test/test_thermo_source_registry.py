from pyThermoLinkDB.builders import ThermoSourceHub, ThermoSourceRegistry
from pyThermoLinkDB.builders.thermo_source_extractor import ThermoSourceExtractor
from pyThermoLinkDB.models import SourceConfig


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
