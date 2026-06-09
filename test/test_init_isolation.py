import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink


def main():
    first = ptdblink.init()
    second = ptdblink.init()

    first.add_thermodb(
        "first-record",
        ptdb.build_thermodb(
            thermodb_name="first-record",
            message="regression test record",
        ),
    )

    assert first.items() == ["first-record"]
    assert second.items() == [], (
        "Fresh ThermoDBHub instance should not inherit thermodb records "
        "from a previous instance."
    )


if __name__ == "__main__":
    main()
