import numpy as np
from pythermodb_settings.models import Component, CustomProperty, CustomConstant

from pyThermoLinkDB.builders import build_custom_model_source


def test_custom_model_source_builds_component_data_and_constants():
    components = [
        Component(name="ethylene", formula="C2H4", state="g"),
        Component(name="ethane", formula="C2H6", state="g"),
        Component(name="carbon dioxide", formula="CO2", state="g"),
    ]

    custom_source = {
        "molecular_weight": {
            "C2H4-g": CustomProperty(value=0.028, unit="kg/mol", symbol="MW"),
            "C2H6-g": CustomProperty(value=0.018, unit="kg/mol", symbol="MW"),
            "CO2-g": CustomProperty(value=0.046, unit="kg/mol", symbol="MW"),
        },
        "reaction_enthalpy": {
            "r1": CustomProperty(value=-85000, unit="J/mol", symbol="dH_rxn"),
            "r2": CustomProperty(value=-80000, unit="J/mol", symbol="dH_rxn"),
        },
        "universal_gas_constant": CustomProperty(
            value=8.314,
            unit="J/mol.K",
            symbol="R"
        ),
        "custom_constant_1": CustomConstant(
            name="custom_constant",
            description="Custom phase label.",
            value="GAS",
            unit=None,
            symbol="CUSTOM_CONST"
        ),
        "custom_constant_2": CustomConstant(
            name="another_custom_constant",
            description="Custom list constant.",
            value=[1, 2, 3],
            unit="units",
            symbol="ANOTHER_CONST"
        ),
        "custom_constant_3": CustomConstant(
            name="third_custom_constant",
            description="Custom dict constant.",
            value={"key1": "value1", "key2": "value2"},
            unit=None,
            symbol="THIRD_CONST"
        ),
    }

    custom_model_src = build_custom_model_source(
        components=components,
        component_key="Formula-State",
        custom_source=custom_source,
        requested_data=["MW"],
        requested_constants=[
            "dH_rxn",
            "R",
            "CUSTOM_CONST",
            "ANOTHER_CONST",
            "THIRD_CONST",
        ],
    )

    assert custom_model_src is not None
    mw_entry = custom_model_src.thermo_src["MW"]
    assert isinstance(mw_entry["value"], np.ndarray)
    np.testing.assert_allclose(mw_entry["value"], [0.028, 0.018, 0.046])
    assert mw_entry["comp"] == {
        "C2H4-g": 0.028,
        "C2H6-g": 0.018,
        "CO2-g": 0.046,
    }
    assert set(mw_entry["src"]) == {"C2H4-g", "C2H6-g", "CO2-g"}
    assert mw_entry["mode"] == ["data"]

    assert custom_model_src.thermo_src["R"]["value"] == 8.314
    assert custom_model_src.thermo_src["R"]["mode"] == ["constants"]
    assert custom_model_src.thermo_src["CUSTOM_CONST"]["value"] == "GAS"
    assert custom_model_src.thermo_src["ANOTHER_CONST"]["value"] == [1, 2, 3]
    assert custom_model_src.thermo_src["THIRD_CONST"]["value"] == {
        "key1": "value1",
        "key2": "value2",
    }
    reaction_values = custom_model_src.thermo_src["dH_rxn"]["value"]
    assert set(reaction_values) == {"r1", "r2"}
    assert reaction_values["r1"].value == -85000

    assert all(
        list(entry) == ["src", "comp", "value", "eq", "mode"]
        for entry in custom_model_src.thermo_src.values()
    )
    assert not hasattr(custom_model_src, "MW_value")
    assert not hasattr(custom_model_src, "dynamic_attributes")
    assert not hasattr(custom_model_src, "config_attributes")


def test_custom_constant_does_not_overwrite_existing_data_attributes():
    components = [
        Component(name="methane", formula="CH4", state="g"),
    ]
    custom_source = {
        "component_value": {
            "CH4-g": CustomProperty(value=16.04, unit="g/mol", symbol="MW"),
        },
        "constant_value": CustomConstant(
            name="conflicting_constant",
            description="Uses the same symbol as component data.",
            value=999.0,
            unit=None,
            symbol="MW",
        ),
    }

    source = build_custom_model_source(
        components=components,
        component_key="Formula-State",
        custom_source=custom_source,
        requested_data=[],
        requested_constants=[],
    )

    assert source is not None
    np.testing.assert_allclose(source.thermo_src["MW"]["value"], [16.04])
    assert source.thermo_src["MW"]["comp"] == {"CH4-g": 16.04}
    assert set(source.thermo_src["MW"]["src"]) == {"CH4-g"}
    assert source.thermo_src["MW"]["mode"] == ["data", "constants"]


def test_custom_thermo_src_preserves_order_and_merges_duplicate_symbols():
    components = [Component(name="methane", formula="CH4", state="g")]
    source = build_custom_model_source(
        components=components,
        component_key="Formula-State",
        custom_source={
            "data_b": {
                "CH4-g": CustomProperty(value=1.0, unit="-", symbol="B"),
            },
            "data_a": {
                "CH4-g": CustomProperty(value=2.0, unit="-", symbol="A"),
            },
            "constant_b": CustomConstant(
                name="duplicate_b",
                description="Conflicts with component data.",
                value=99.0,
                unit=None,
                symbol="B",
            ),
            "constant_c": CustomConstant(
                name="constant_c",
                description="Independent constant.",
                value=3.0,
                unit=None,
                symbol="C",
            ),
        },
        requested_data=["B", "A"],
        requested_constants=["B", "C"],
    )

    assert source is not None
    assert list(source.thermo_src) == ["B", "A", "C"]
    assert source.thermo_src["B"]["mode"] == ["data", "constants"]
    np.testing.assert_allclose(source.thermo_src["B"]["value"], [1.0])
    assert source.thermo_src["C"]["mode"] == ["constants"]
    assert source.thermo_src["C"]["value"] == 3.0
