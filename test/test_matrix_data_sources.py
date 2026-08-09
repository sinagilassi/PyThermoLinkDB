from pythermodb_settings.models import Component

from pyThermoLinkDB.thermo.matrix_data_sources import MatrixDataSourcesCore


class FakeSource:
    pass


class FakeMatrixDataSource:
    def __init__(
        self,
        components,
        source,
        mixture_key="Name",
        extract_list=None,
        delimiter="|",
        case=None,
    ):
        self.components = components
        self.source = source
        self.mixture_key = mixture_key
        self.extract_list = extract_list
        self.delimiter = delimiter
        self.case = case

    def summary(self):
        return {
            prop_name: prop_name != "missing"
            for prop_name in self.extract_list or []
        }

    def build_status(self):
        return all(self.summary().values())


def test_matrix_data_sources_builds_sources_by_mixture_id(monkeypatch):
    monkeypatch.setattr(
        "pyThermoLinkDB.thermo.matrix_data_sources.MatrixDataSourceCore",
        FakeMatrixDataSource,
    )
    methanol = Component(name="methanol", formula="CH3OH", state="l")
    ethanol = Component(name="ethanol", formula="C2H5OH", state="l")

    matrix_sources = MatrixDataSourcesCore(
        mixture_components=[[methanol, ethanol]],
        source=FakeSource(),
        mixture_key="Name",
        extract_list=["alpha"],
    )

    assert list(matrix_sources.src) == ["ethanol|methanol"]
    assert matrix_sources.summary() == {
        "ethanol|methanol": {"alpha": True},
    }
    assert matrix_sources.build_status() is True
    assert matrix_sources.select("ethanol|methanol") is matrix_sources.src["ethanol|methanol"]


def test_matrix_data_sources_reports_failed_property(monkeypatch):
    monkeypatch.setattr(
        "pyThermoLinkDB.thermo.matrix_data_sources.MatrixDataSourceCore",
        FakeMatrixDataSource,
    )
    methanol = Component(name="methanol", formula="CH3OH", state="l")
    ethanol = Component(name="ethanol", formula="C2H5OH", state="l")

    matrix_sources = MatrixDataSourcesCore(
        mixture_components=[[methanol, ethanol]],
        source=FakeSource(),
        mixture_key="Name",
        extract_list=["alpha", "missing"],
    )

    assert matrix_sources.summary() == {
        "ethanol|methanol": {"alpha": True, "missing": False},
    }
    assert matrix_sources.build_status() is False
    assert matrix_sources.select("unknown") is None
