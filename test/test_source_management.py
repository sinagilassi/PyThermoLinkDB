from types import SimpleNamespace

import numpy as np

from pyThermoLinkDB.builders import ThermoCustomSource, ThermoSourceValidator


def make_model_source(thermo_src, component_ids=None):
    return SimpleNamespace(
        thermo_src=thermo_src,
        requested_data=["Tc"],
        requested_equations=["Cp"],
        requested_constants=["R"],
        component_references={"component_ids": component_ids or ["A", "B"]},
    )


def test_validator_returns_none_when_no_sources_are_available():
    validator = ThermoSourceValidator(source=SimpleNamespace())

    assert validator.validate() is None


def test_validator_reports_missing_component_data_without_raising():
    source = make_model_source(
        thermo_src={
            "Tc": {
                "src": {"A": object()},
                "comp": {"A": 300.0},
                "value": np.array([300.0]),
                "eq": None,
                "mode": ["data"],
            },
            "Cp": {
                "src": None,
                "comp": None,
                "value": None,
                "eq": {"A": object(), "B": object()},
                "mode": ["equation"],
            },
            "R": {
                "src": object(),
                "comp": None,
                "value": 8.314,
                "eq": None,
                "mode": ["constants"],
            },
        }
    )

    report = ThermoSourceValidator(source=source).validate()

    assert report is not None
    assert report.is_valid is False
    assert report.all_requested_available is False
    assert report.all_components_available is False
    assert report.missing_data == {"Tc": ["B"]}


def test_validator_accepts_complete_model_source():
    source = make_model_source(
        thermo_src={
            "Tc": {
                "src": {"A": object(), "B": object()},
                "comp": {"A": 300.0, "B": 400.0},
                "value": np.array([300.0, 400.0]),
                "eq": None,
                "mode": ["data"],
            },
            "Cp": {
                "src": None,
                "comp": None,
                "value": None,
                "eq": {"A": object(), "B": object()},
                "mode": ["equation"],
            },
            "R": {
                "src": object(),
                "comp": None,
                "value": 8.314,
                "eq": None,
                "mode": ["constants"],
            },
        }
    )

    report = ThermoSourceValidator(source=source).validate()

    assert report is not None
    assert report.is_valid is True
    assert report.summary()["error_count"] == 0
    assert report.all_requested_available is True
    assert report.all_components_available is True


def test_source_exposes_validation_report_and_quick_checks():
    source = ThermoCustomSource(
        components=[],
        component_key="Formula-State",
        requested_data=["MW"],
        requested_constants=[],
        component_references={"component_ids": ["CH4-g"]},
    )
    source.thermo_src = {
        "MW": {
            "src": {"CH4-g": object()},
            "comp": {"CH4-g": 16.04},
            "value": np.array([16.04]),
            "eq": None,
            "mode": ["data"],
        }
    }

    report = source.validate_thermo_src()

    assert report is source.validation_details()
    assert source.is_valid_build() is True
    assert source.has_all_requested() is True
    assert source.has_all_components() is True
    assert source.validation_summary()["all_requested_available"] is True
