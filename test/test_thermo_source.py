from types import SimpleNamespace

from pyThermoLinkDB.builders import ThermoSource, build_thermo_source


def make_container(model=None, custom=None, description="container"):
    components = [SimpleNamespace(name="A"), SimpleNamespace(name="B")]
    source = ThermoSource(
        components=components,
        component_key="Formula-State",
        thermo_model_source=model,
        thermo_custom_source=custom,
        description=description,
    )
    return source, components


def test_thermo_source_holds_both_sources_by_identity():
    model = SimpleNamespace(thermo_src={"Tc": {"value": 300.0}})
    custom = SimpleNamespace(thermo_src={"R": {"value": 8.314}})

    source, components = make_container(model=model, custom=custom)

    assert source.thermo_model_source is model
    assert source.thermo_custom_source is custom
    assert source.components is components
    assert source.component_key == "Formula-State"
    assert source.description == "container"


def test_thermo_source_allows_either_source_to_be_none():
    model = SimpleNamespace(thermo_src={})
    custom = SimpleNamespace(thermo_src={})

    model_only, _ = make_container(model=model)
    custom_only, _ = make_container(custom=custom)

    assert model_only.thermo_model_source is model
    assert model_only.thermo_custom_source is None
    assert custom_only.thermo_model_source is None
    assert custom_only.thermo_custom_source is custom


def test_thermo_source_hub_types_uses_non_empty_groups():
    model = SimpleNamespace(thermo_src={"Tc": {"value": 300.0}})
    custom = SimpleNamespace(thermo_src={})

    source, _ = make_container(model=model, custom=custom)

    assert source.thermo_source_hub_types == "model_source"


def test_thermo_source_hub_types_raises_when_groups_are_empty():
    model = SimpleNamespace(thermo_src={})
    custom = SimpleNamespace(thermo_src={})

    source, _ = make_container(model=model, custom=custom)

    try:
        source.thermo_source_hub_types
    except ValueError as exc:
        assert str(exc) == "No thermo source is available in the hub."
    else:
        raise AssertionError(
            "Expected thermo_source_hub_types to raise ValueError.")


def test_thermo_source_has_no_management_api():
    source, _ = make_container()
    removed_names = (
        "registry",
        "resolver",
        "validator",
        "source",
        "refresh",
        "_extract_attributes",
        "get",
        "resolve",
        "validate",
        "to_dict",
    )

    assert all(not hasattr(source, name) for name in removed_names)


def test_thermo_source_delegates_validation_helpers():
    model = SimpleNamespace(
        validate_thermo_src=lambda: "model-report",
        validation_summary=lambda: {"is_valid": True},
        is_valid_build=lambda: True,
        has_all_requested=lambda: True,
        has_all_components=lambda: True,
    )
    custom = SimpleNamespace(
        validate_thermo_src=lambda: "custom-report",
        validation_summary=lambda: {"is_valid": False},
        is_valid_build=lambda: False,
        has_all_requested=lambda: False,
        has_all_components=lambda: False,
    )

    source, _ = make_container(model=model, custom=custom)

    assert source.validate_model_source() == "model-report"
    assert source.validate_custom_source() == "custom-report"
    assert source.validate_sources() == {
        "model_source": "model-report",
        "custom_source": "custom-report",
    }
    assert source.validation_summary() == {
        "model_source": {"is_valid": True},
        "custom_source": {"is_valid": False},
    }
    assert source.is_model_source_valid() is True
    assert source.is_custom_source_valid() is False
    assert source.has_all_model_requested() is True
    assert source.has_all_custom_requested() is False
    assert source.has_all_model_components() is True
    assert source.has_all_custom_components() is False


def test_builder_rejects_missing_model_and_custom_sources():
    result = build_thermo_source(
        components=[],
        component_key="Formula-State",
        model_source=None,
        custom_source=None,
        model_source_config=None,
        custom_source_config=None,
    )

    assert result is None
