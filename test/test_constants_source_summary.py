from pyThermoLinkDB.thermo.constants_source import ConstantsSourceCore


class FakeSource:
    constantssource = {
        "R": {
            "value": 8.314,
            "unit": "J/mol.K",
            "symbol": "R",
        },
    }
    constantssource_symbols = {}


def test_summary_reports_extraction_status_for_requested_constants():
    constants_source = ConstantsSourceCore(
        source=FakeSource(),
        extract_list=["R", "missing"],
    )

    assert constants_source.summary() == {"R": True, "missing": False}
    assert constants_source.build_status() is False


def test_summary_is_empty_and_build_status_is_true_without_extract_list():
    constants_source = ConstantsSourceCore(source=FakeSource())

    assert constants_source.summary() == {}
    assert constants_source.build_status() is True


def test_build_status_is_true_when_all_requested_constants_are_extracted():
    constants_source = ConstantsSourceCore(
        source=FakeSource(),
        extract_list=["R"],
    )

    assert constants_source.build_status() is True
