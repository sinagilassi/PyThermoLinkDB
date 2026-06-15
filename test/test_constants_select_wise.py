from pyThermoLinkDB.thermo.constants_source import ConstantsSourceCore


class FakeSource:
    constantssource = {
        "R": {
            "value": 8.314,
            "unit": "J/mol.K",
            "symbol": "R",
        },
        "label": {
            "value": "methanol",
            "unit": None,
            "symbol": "label_sym",
        },
        "mapping": {
            "value": {"a": 1},
            "unit": "kJ/mol",
            "symbol": "mapping_sym",
        },
        "items": {
            "value": [1, 2],
            "unit": None,
            "symbol": "items_sym",
        },
        "empty": {
            "value": None,
            "unit": None,
            "symbol": "empty_sym",
        },
        "list_value": {
            "value": [1, 2],
            "unit": "",
            "symbol": "x",
        },
    }
    constantssource_symbols = {
        "label": {
            "symbol": "label_sym",
        },
    }

    def constants_extractor(self, constant_name):
        return self.constantssource.get(constant_name)

    def constant_symbol(self, constant_name):
        return self.constantssource_symbols.get(constant_name)

    def is_constant_available(self, constant_name):
        return constant_name in self.constantssource


def test_select_wise_preserves_arbitrary_constant_values():
    source = ConstantsSourceCore(FakeSource())

    assert source.select_wise("R").value == 8.314
    assert source.select_wise("label").value == "methanol"
    assert source.select_wise("label").symbol == "label_sym"
    assert source.select_wise("label").unit is None
    assert source.select_wise("mapping").value == {"a": 1}
    assert source.select_wise("mapping").unit == "kJ/mol"
    assert source.select_wise("items").value == [1, 2]
    assert source.select_wise("items").unit is None
    assert source.select_wise("empty").value is None
    assert source.select_wise("list_value").value == [1, 2]


def test_select_stays_numeric_property_selector():
    source = ConstantsSourceCore(FakeSource())

    assert source.select("R").value == 8.314
    assert source.select("label") is None
    assert source.select_wise("missing") is None
