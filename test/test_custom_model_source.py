import numpy as np
from pythermodb_settings.models import Component, CustomProperty

from pyThermoLinkDB.builders import build_custom_model_source
from pyThermoLinkDB.models import CustomConstant


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
        thermo_data=["MW"],
        thermo_constants=[
            "dH_rxn",
            "R",
            "CUSTOM_CONST",
            "ANOTHER_CONST",
            "THIRD_CONST",
        ],
    )

    assert custom_model_src is not None
    assert isinstance(custom_model_src.MW_value, np.ndarray)
    np.testing.assert_allclose(custom_model_src.MW_value, [0.028, 0.018, 0.046])
    assert custom_model_src.MW_comp == {
        "C2H4-g": 0.028,
        "C2H6-g": 0.018,
        "CO2-g": 0.046,
    }
    assert set(custom_model_src.MW_src) == {"C2H4-g", "C2H6-g", "CO2-g"}

    assert custom_model_src.R_value == 8.314
    assert custom_model_src.CUSTOM_CONST_value == "GAS"
    assert custom_model_src.ANOTHER_CONST_value == [1, 2, 3]
    assert custom_model_src.THIRD_CONST_value == {
        "key1": "value1",
        "key2": "value2",
    }
    assert set(custom_model_src.dH_rxn_value) == {"r1", "r2"}
    assert custom_model_src.dH_rxn_value["r1"].value == -85000

    dynamic_attrs = custom_model_src.dynamic_attributes()
    assert dynamic_attrs["thermo_data"]["MW"]["MW_value"] is custom_model_src.MW_value
    assert dynamic_attrs["thermo_constants"]["R"]["R_value"] == 8.314
