import numpy as np

from pyThermoLinkDB.builders.thermo_model_source import ThermoModelSource
from pyThermoLinkDB.models.component_models import ConstantResult


class StubConstantsSource:
    constants = ["R"]

    def select(self, symbol: str) -> ConstantResult:
        return ConstantResult(value=8.314, unit="J/mol.K", symbol=symbol)


class StubComponentConstantsSource:
    constants = ["data_symbol", "equation_symbol"]

    def select(self, symbol: str) -> ConstantResult:
        values = {
            "data_symbol": {"A": 10.0, "B": 20.0},
            "equation_symbol": {
                "A": {"value": 30.0, "unit": "J/mol"},
                "B": {"value": 40.0, "unit": "J/mol"},
            },
        }
        return ConstantResult(value=values[symbol], unit="J/mol", symbol=symbol)


class StubDataSource:
    props = ["R"]


class StubMissingEquationConstantSource:
    constants = ["equation_symbol"]

    def select(self, symbol: str) -> None:
        return None


def test_constant_symbol_does_not_overwrite_existing_data_attributes():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=[],
        requested_equations=[],
        requested_constants=[],
        component_references={"component_ids": []},
    )
    # A non-empty source lets the data configuration create the attributes;
    # component contents are irrelevant to this collision test.
    source.thermo_data_source = {"component": StubDataSource()}
    source.thermo_constants_source = StubConstantsSource()

    source.config_attributes()

    assert source.R_src == {}
    assert isinstance(source.R_value, np.ndarray)
    assert source.R_value.size == 0
    assert source.used_symbols == ["R"]
    assert source.requested_constants == ["R"]


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
    source.data_symbol_src = original_data_src
    source.data_symbol_comp = {"A": 1.0, "B": 2.0}
    source.data_symbol_value = np.array([1.0, 2.0])
    source.equation_symbol_src = original_equation_src
    source.equation_symbol_comp = None
    source.equation_symbol_value = None
    source.equation_symbol_eq = original_equation_src
    source.used_symbols = ["data_symbol", "equation_symbol"]
    source.thermo_constants_source = StubComponentConstantsSource()

    source._config_constant_attributes()

    assert isinstance(source.data_symbol_src, ConstantResult)
    assert source.data_symbol_comp == {"A": 10.0, "B": 20.0}
    np.testing.assert_allclose(source.data_symbol_value, [10.0, 20.0])
    assert source.equation_symbol_src is original_equation_src
    assert source.equation_symbol_comp == {"A": 30.0, "B": 40.0}
    np.testing.assert_allclose(source.equation_symbol_value, [30.0, 40.0])
    assert source.equation_symbol_eq is original_equation_src
    assert source.requested_constants == []
    assert "equation_symbol" not in source.dynamic_attributes()["thermo_constants"]


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

    source.config_attributes()

    assert source.requested_data == ["data_symbol"]
    assert source.requested_constants == []
    assert source.used_symbols == ["data_symbol"]
    assert source.data_symbol_comp == {"A": 10.0, "B": 20.0}
    np.testing.assert_allclose(source.data_symbol_value, [10.0, 20.0])
    assert "data_symbol" not in source.dynamic_attributes()["thermo_constants"]


def test_equation_symbol_is_removed_from_constants_when_constant_is_missing():
    source = ThermoModelSource(
        components=[],
        component_key="Name",
        requested_data=[],
        requested_equations=["equation_symbol"],
        requested_constants=["equation_symbol"],
        component_references={"component_ids": []},
    )
    source.used_symbols = ["equation_symbol"]
    source.thermo_constants_source = StubMissingEquationConstantSource()

    source._config_constant_attributes()

    assert source.requested_constants == []
    assert "equation_symbol" not in source.dynamic_attributes()["thermo_constants"]
