from pythermodb_settings.models import Component

from pyThermoLinkDB.thermo.data_source import DataSourceCore


class FakeSource:
    def __init__(self, component_data):
        self.component_data = component_data

    def component_data_extractor(self, component_id):
        return self.component_data


def test_summary_reports_build_status_for_each_requested_property():
    data_source = DataSourceCore(
        component=Component(name="methane", formula="CH4", state="g"),
        source=FakeSource({
            "MW": {"value": 16.04, "unit": "g/mol", "symbol": "MW"},
        }),
        extract_list=["MW", "Tc"],
    )

    assert data_source.summary() == {"MW": True, "Tc": False}
    assert data_source.props == ["MW"]


def test_summary_is_empty_without_requested_properties():
    data_source = DataSourceCore(
        component=Component(name="methane", formula="CH4", state="g"),
        source=FakeSource({
            "MW": {"value": 16.04, "unit": "g/mol", "symbol": "MW"},
        }),
    )

    assert data_source.summary() == {}
