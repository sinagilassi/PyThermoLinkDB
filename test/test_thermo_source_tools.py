from typing import cast

from pythermodb_settings.models import Component, CustomProperty

from pyThermoLinkDB.thermo import EquationSourceCore
from pyThermoLinkDB.utils.thermo_source_tools import map_eq, map_prop


def _components():
    return [
        Component(name="ethylene", formula="C2H4", state="g"),
        Component(name="ethane", formula="C2H6", state="g"),
        Component(name="carbon dioxide", formula="CO2", state="g"),
    ]


def test_map_prop_orders_results_by_components_with_unknown_input_key():
    components = _components()
    data = {
        "CO2-g": CustomProperty(value=0.044, unit="kg/mol", symbol="MW"),
        "ethylene-g": CustomProperty(value=0.028, unit="kg/mol", symbol="MW"),
        "ethane": CustomProperty(value=0.030, unit="kg/mol", symbol="MW"),
    }

    result = map_prop(
        data=data,
        components=components,
        component_key="Formula-State",
    )

    assert result == (
        {
            "C2H4-g": 0.028,
            "C2H6-g": 0.030,
            "CO2-g": 0.044,
        },
        [0.028, 0.030, 0.044],
    )


def test_map_prop_skips_missing_components_but_preserves_order():
    components = _components()
    data = {
        "CO2-g": CustomProperty(value=0.044, unit="kg/mol", symbol="MW"),
        "unknown-g": CustomProperty(value=1.0, unit="kg/mol", symbol="MW"),
        "ethylene-g": CustomProperty(value=0.028, unit="kg/mol", symbol="MW"),
    }

    result = map_prop(
        data=data,
        components=components,
        component_key="Formula-State",
    )

    assert result == (
        {
            "C2H4-g": 0.028,
            "CO2-g": 0.044,
        },
        [0.028, 0.044],
    )


def test_map_eq_orders_results_by_components_with_unknown_input_key():
    components = _components()
    ethylene_eq = cast(EquationSourceCore, object())
    ethane_eq = cast(EquationSourceCore, object())
    carbon_dioxide_eq = cast(EquationSourceCore, object())
    data = {
        "CO2-g": carbon_dioxide_eq,
        "ethylene-g": ethylene_eq,
        "ethane": ethane_eq,
    }

    result = map_eq(
        data=data,
        components=components,
        component_key="Formula-State",
    )

    assert result == (
        {
            "C2H4-g": ethylene_eq,
            "C2H6-g": ethane_eq,
            "CO2-g": carbon_dioxide_eq,
        },
        [ethylene_eq, ethane_eq, carbon_dioxide_eq],
    )


def test_map_eq_empty_data_returns_empty_tuple_parts():
    result = map_eq(
        data={},
        components=_components(),
        component_key="Formula-State",
    )

    assert result == ({}, [])
