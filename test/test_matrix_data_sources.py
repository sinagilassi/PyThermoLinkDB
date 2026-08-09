from pythermodb_settings.models import Component

import pyThermoLinkDB
from pyThermoLinkDB.models import ModelSource
from pyThermoLinkDB.thermo.main import mkmdt, mkmdts, mkmdtss


def test_mkmdt_builds_one_property_matrix_data_source(monkeypatch):
    built_args = []

    class FakeMatrixDataSourceCore:
        def __init__(self, **kwargs):
            built_args.append(kwargs)

    monkeypatch.setattr(
        "pyThermoLinkDB.thermo.main.MatrixDataSourceCore",
        FakeMatrixDataSourceCore,
    )
    methanol = Component(name="methanol", formula="CH3OH", state="l")
    ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
    model_source = ModelSource(data_source={}, equation_source={})

    matrix_source = mkmdt(
        name="alpha",
        components=[methanol, ethanol],
        model_source=model_source,
        mixture_key="Name",
    )

    assert matrix_source is not None
    assert isinstance(matrix_source, FakeMatrixDataSourceCore)
    assert built_args[0]["prop_name"] == "alpha"
    assert built_args[0]["components"] == [methanol, ethanol]


def test_mkmdt_returns_none_for_invalid_inputs():
    model_source = ModelSource(data_source={}, equation_source={})
    methanol = Component(name="methanol", formula="CH3OH", state="l")

    assert mkmdt(name="", components=[methanol], model_source=model_source) is None
    assert mkmdt(name="alpha", components=[], model_source=model_source) is None
    assert mkmdt(name="alpha", components=[methanol], model_source=None) is None


def test_mkmdts_returns_matrix_data_sources_core(monkeypatch):
    built_args = []

    class FakeMatrixDataSourcesCore:
        def __init__(self, **kwargs):
            built_args.append(kwargs)

    monkeypatch.setattr(
        "pyThermoLinkDB.thermo.main.MatrixDataSourcesCore",
        FakeMatrixDataSourcesCore,
    )
    methanol = Component(name="methanol", formula="CH3OH", state="l")
    ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
    model_source = ModelSource(data_source={}, equation_source={})

    matrix_sources = mkmdts(
        components=[methanol, ethanol],
        model_source=model_source,
        mixture_key="Name",
        extract_list=["alpha", "b"],
    )

    assert matrix_sources is not None
    assert isinstance(matrix_sources, FakeMatrixDataSourcesCore)
    assert built_args[0]["components"] == [methanol, ethanol]
    assert built_args[0]["extract_list"] == ["alpha", "b"]


def test_mkmdtss_returns_matrix_data_sources_core_by_mixture_id(monkeypatch):
    built_args = []

    class FakeMatrixDataSourcesCore:
        def __init__(self, **kwargs):
            built_args.append(kwargs)
            self.mixture_name = "ethanol|methanol"

        def build_status(self):
            return True

        def summary(self):
            return {"alpha": True}

    monkeypatch.setattr(
        "pyThermoLinkDB.thermo.main.MatrixDataSourcesCore",
        FakeMatrixDataSourcesCore,
    )
    methanol = Component(name="methanol", formula="CH3OH", state="l")
    ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
    model_source = ModelSource(data_source={}, equation_source={})

    matrix_sources = mkmdtss(
        mixture_components=[[methanol, ethanol]],
        model_source=model_source,
        mixture_key="Name",
        extract_list=["alpha"],
        check_build=True,
    )

    assert matrix_sources is not None
    assert list(matrix_sources) == ["ethanol|methanol"]
    assert isinstance(
        matrix_sources["ethanol|methanol"],
        FakeMatrixDataSourcesCore,
    )
    assert built_args[0]["components"] == [methanol, ethanol]
    assert built_args[0]["extract_list"] == ["alpha"]


def test_mkmdtss_is_publicly_exported():
    assert pyThermoLinkDB.mkmdtss is mkmdtss
