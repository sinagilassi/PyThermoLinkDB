import numpy as np
from pythermodb_settings.models import CustomConstant
from pyThermoLinkDB.builders.thermo_model_source import ThermoModelSource


class StubConstantsSource:
    constants = ["R"]

    def select(self, symbol: str) -> CustomConstant:
        return CustomConstant(value=8.314, unit="J/mol.K", symbol=symbol)


class StubComponentConstantsSource:
    constants = ["data_symbol", "equation_symbol"]

    def select(self, symbol: str) -> CustomConstant:
        values = {
            "data_symbol": {"A": 10.0, "B": 20.0},
            "equation_symbol": {
                "A": {"value": 30.0, "unit": "J/mol"},
                "B": {"value": 40.0, "unit": "J/mol"},
            },
        }
        return CustomConstant(value=values[symbol], unit="J/mol", symbol=symbol)


class StubDataSource:
    props = ["R"]


class StubMissingEquationConstantSource:
    constants = ["equation_symbol"]

    def select(self, symbol: str) -> None:
        return None


def test_constant_symbol_does_not_overwrite_existing_data_entry():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=[],
        requested_equations=[],
        requested_constants=[],
        component_references={"component_ids": []},
    )
    # A non-empty source lets the data population create the entry;
    # component contents are irrelevant to this collision test.
    source.thermo_data_source = {"component": StubDataSource()}
    source.thermo_constants_source = StubConstantsSource()

    source.populate_thermo_src()

    assert source.thermo_src["R"]["src"] == {}
    assert isinstance(source.thermo_src["R"]["value"], np.ndarray)
    assert source.thermo_src["R"]["value"].size == 0
    assert source.thermo_src["R"]["mode"] == ["data", "constants"]
    assert source.requested_constants == ["R"]
    assert not hasattr(source, "R_src")


def test_component_constants_merge_with_existing_data_and_equations():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=["data_symbol"],
        requested_equations=["equation_symbol"],
        requested_constants=["data_symbol", "equation_symbol"],
        component_references={"component_ids": ["A", "B"]},
    )
    original_data_src = {"original": object()}
    original_equation_src = {"equation": object()}
    source._initialize_thermo_src()
    source.thermo_src["data_symbol"].update({
        "src": original_data_src,
        "comp": {"A": 1.0, "B": 2.0},
        "value": np.array([1.0, 2.0]),
    })
    source.thermo_src["equation_symbol"].update({
        "src": original_equation_src,
        "eq": original_equation_src,
    })
    source.thermo_constants_source = StubComponentConstantsSource()

    source._populate_constants()

    data_entry = source.thermo_src["data_symbol"]
    equation_entry = source.thermo_src["equation_symbol"]
    assert isinstance(data_entry["src"], CustomConstant)
    assert data_entry["mode"] == ["data", "constants"]
    assert data_entry["comp"] == {"A": 10.0, "B": 20.0}
    np.testing.assert_allclose(data_entry["value"], [10.0, 20.0])
    assert equation_entry["src"] is original_equation_src
    assert equation_entry["mode"] == ["equation", "constants"]
    assert equation_entry["comp"] == {"A": 30.0, "B": 40.0}
    np.testing.assert_allclose(equation_entry["value"], [30.0, 40.0])
    assert equation_entry["eq"] is original_equation_src
    assert source.requested_constants == []


def test_component_constant_is_data_even_without_regular_data_source():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=["data_symbol"],
        requested_equations=[],
        requested_constants=["data_symbol"],
        component_references={"component_ids": ["A", "B"]},
    )
    source.thermo_constants_source = StubComponentConstantsSource()

    source.populate_thermo_src()

    assert source.requested_data == ["data_symbol"]
    assert source.requested_constants == []
    assert source.thermo_src["data_symbol"]["mode"] == ["data", "constants"]
    assert source.thermo_src["data_symbol"]["comp"] == {"A": 10.0, "B": 20.0}
    np.testing.assert_allclose(
        source.thermo_src["data_symbol"]["value"], [10.0, 20.0]
    )


def test_equation_symbol_is_removed_from_constants_when_constant_is_missing():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=[],
        requested_equations=["equation_symbol"],
        requested_constants=["equation_symbol"],
        component_references={"component_ids": []},
    )
    source.thermo_constants_source = StubMissingEquationConstantSource()
    source._initialize_thermo_src()

    source._populate_constants()

    assert source.requested_constants == []
    assert source.thermo_src["equation_symbol"] == {
        "src": None,
        "comp": None,
        "value": None,
        "eq": None,
        "mode": ["equation", "constants"],
    }


def test_thermo_src_has_fixed_shape_and_preserves_symbol_order():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=["B", "A"],
        requested_equations=["A", "C"],
        requested_constants=["B", "D"],
        component_references={"component_ids": []},
    )

    source.populate_thermo_src()

    assert list(source.thermo_src) == ["B", "A", "C", "D"]
    assert all(
        list(entry) == ["src", "comp", "value", "eq", "mode"]
        for entry in source.thermo_src.values()
    )
    assert not hasattr(source, "dynamic_attributes")
    assert not hasattr(source, "config_attributes")
