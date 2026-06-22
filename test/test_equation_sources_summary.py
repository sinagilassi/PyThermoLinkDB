from pyThermoLinkDB.thermo.equation_sources import EquationSourcesCore


def make_equation_sources(build_list, src):
    equation_sources = EquationSourcesCore.__new__(EquationSourcesCore)
    equation_sources.build_list = build_list
    equation_sources._src = src
    return equation_sources


def test_summary_reports_build_status_for_each_requested_equation():
    equation_sources = make_equation_sources(
        build_list=["VaPr", "Cp_IG", "Missing"],
        src={"VaPr": object(), "Cp_IG": None},
    )

    assert equation_sources.summary() == {
        "VaPr": True,
        "Cp_IG": False,
        "Missing": False,
    }
    assert equation_sources.build_status() is False


def test_summary_is_empty_and_build_status_is_true_without_build_list():
    equation_sources = make_equation_sources(build_list=None, src={})

    assert equation_sources.summary() == {}
    assert equation_sources.build_status() is True


def test_build_status_is_true_when_all_requested_equations_are_built():
    equation_sources = make_equation_sources(
        build_list=["VaPr", "Cp_IG"],
        src={"VaPr": object(), "Cp_IG": object()},
    )

    assert equation_sources.build_status() is True
