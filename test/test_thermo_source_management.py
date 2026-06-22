from types import SimpleNamespace

import pytest

from pyThermoLinkDB.builders import ThermoSource


class StubModelSource:
    def __init__(self, attributes, component_ids=("A-g", "B-g")):
        self.attributes = attributes
        self.component_references = {"component_ids": list(component_ids)}
        self.requested_data = list(attributes.get("thermo_data", {}))
        self.requested_equations = list(attributes.get("thermo_equations", {}))
        self.requested_constants = list(attributes.get("thermo_constants", {}))

    @property
    def thermo_src(self):
        result = {}
        for entries in self.attributes.values():
            for symbol, attributes in entries.items():
                entry_ = result.setdefault(
                    symbol,
                    {"src": None, "comp": None, "value": None, "eq": None},
                )
                for name, value in attributes.items():
                    entry_[name.removeprefix(f"{symbol}_")] = value
        return result


class StubCustomSource:
    def __init__(self, attributes, component_ids=("A-g", "B-g")):
        self.attributes = attributes
        self.component_references = {"component_ids": list(component_ids)}

    def dynamic_attributes(self):
        return self.attributes


def entry(symbol, value, components=None):
    components = components or {"A-g": value, "B-g": value}
    return {
        f"{symbol}_src": {},
        f"{symbol}_comp": components,
        f"{symbol}_value": value,
    }


def make_source(model=None, custom=None, **kwargs):
    return ThermoSource(
        components=[SimpleNamespace(), SimpleNamespace()],
        component_key="Formula-State",
        thermo_model_source=StubModelSource(model) if model is not None else None,
        thermo_custom_source=StubCustomSource(custom) if custom is not None else None,
        **kwargs,
    )


def test_registry_uses_custom_keys_and_supports_lookup():
    source = make_source(
        model={"thermo_data": {"MW": entry("MW", 10)}},
        custom={"thermo_constants": {"R": entry("R", 8.314)}},
        model_source_key="database",
        custom_source_key="overrides",
    )

    assert set(source.source) == {"database", "overrides"}
    assert source.get("MW", source_type="model") == 10
    assert source.get("R", category="constants", source_type="custom") == 8.314
    assert source.has("MW")
    assert source.list_symbols() == ["MW", "R"]


def test_resolver_applies_precedence_and_reports_conflicts():
    source = make_source(
        model={"thermo_data": {"MW": entry("MW", 10)}},
        custom={"thermo_data": {"MW": entry("MW", 20)}},
    )

    with pytest.raises(ValueError, match="ambiguous"):
        source.registry.get("MW")

    assert source.resolve("MW") == 20
    assert source.resolve("MW", precedence=("model", "custom")) == 10
    assert source.find_conflicts() == {"thermo_data": ["MW"]}
    exported = source.to_dict()
    assert exported["model_source"]["thermo_data"]["MW"]["MW_value"] == 10
    assert exported["custom_source"]["thermo_data"]["MW"]["MW_value"] == 20


def test_validator_reports_missing_and_incomplete_data():
    source = make_source(
        model={
            "thermo_data": {
                "MW": entry("MW", 10, components={"A-g": 10}),
            }
        },
    )

    result = source.validate(required={"data": ["MW", "Tc"]})

    assert not result.valid
    assert result.missing == {"thermo_data": ["Tc"]}
    assert any("incomplete" in error for error in result.errors)
    assert source.get_component("MW", "A-g", source_type="model") == 10
    assert not source.is_complete("MW", "model")


def test_refresh_mutation_summary_and_copy():
    model = StubModelSource({"thermo_constants": {"R": entry("R", 8.0)}})
    source = ThermoSource([], "Formula-State", model, None)
    model.attributes["thermo_constants"]["R"]["R_value"] = 8.314

    source.refresh()

    assert source.get("R") == 8.314
    assert source.summary()["sources"] == {
        "model_source": True,
        "custom_source": False,
    }
    clone = source.copy()
    source.remove_source("model")
    assert clone.has("R")
    assert not source.has("R")
