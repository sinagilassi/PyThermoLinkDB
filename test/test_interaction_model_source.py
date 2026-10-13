import pyThermoDB as ptdb
from pyThermoDB import TableEquation, TableInteractionData
from pythermodb_settings.models import Component

import pyThermoLinkDB
from pyThermoLinkDB import (
    build_interaction_model_source,
    build_model_source,
)
from pyThermoLinkDB.models import (
    ComponentModelSource,
    ConstantsModelSource,
    MixtureModelSource,
)


class StubTableEquation(TableEquation):
    """Minimal TableEquation used to verify aggregation by identity."""

    def __init__(self, name):
        self.name = name

    def eq_return(self):
        return {}

    def eq_args(self):
        return {}

    def get_return_symbols(self):
        return []

    def get_arg_symbols(self):
        return []


REFERENCE_CONTENT = """
REFERENCES:
  PITZER-EXAMPLE:
    DATABOOK-ID: 1
    TABLES:
      Pitzer interaction parameters:
        TABLE-ID: 1
        DESCRIPTION: Scalar ternary interaction parameters.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [null, null, psi, zeta]
          UNIT: [null, null, 1, mol/kg]
        VALUES:
          - [1, "potassium-ion|sodium-ion|chloride-ion", -0.0018, 0.25]
          - [2, "sodium-ion|potassium-ion|chloride-ion", 0.0, null]
"""


def _build_interaction_thermodb():
    components = [
        Component(name="sodium-ion", formula="Na{+}", state="aq"),
        Component(name="potassium-ion", formula="K{+}", state="aq"),
        Component(name="chloride-ion", formula="Cl{-}", state="aq"),
    ]
    result = ptdb.build_interaction_thermodb_from_reference(
        components=components,
        reference_content=REFERENCE_CONTENT,
    )
    assert result is not None
    assert result.thermodb.check()
    return components, result


def test_build_interaction_model_source_preserves_scalar_table_behavior():
    components, interaction_thermodb = _build_interaction_thermodb()

    source = build_interaction_model_source(interaction_thermodb)

    assert source.components == components
    assert source.equation_source == {
        mixture_id: {} for mixture_id in source.data_source
    }
    assert set(source.data_source) == {
        "chloride-ion|potassium-ion|sodium-ion",
        "Cl{-}|K{+}|Na{+}",
        "chloride-ion-aq|potassium-ion-aq|sodium-ion-aq",
        "Cl{-}-aq|K{+}-aq|Na{+}-aq",
    }

    interaction = source.data_source[
        "chloride-ion|potassium-ion|sodium-ion"
    ]["psi"]
    assert isinstance(interaction, TableInteractionData)
    assert source.data_source[
        "chloride-ion|potassium-ion|sodium-ion"
    ]["zeta"] is interaction

    assert interaction.get(
        "psi", "potassium-ion|sodium-ion|chloride-ion"
    ) == -0.0018
    assert interaction.get(
        "psi", "sodium-ion|potassium-ion|chloride-ion"
    ) == 0.0
    assert interaction.get(
        "zeta", "sodium-ion|potassium-ion|chloride-ion"
    ) is None
    assert interaction.get(
        "zeta",
        "sodium-ion|potassium-ion|chloride-ion",
        symmetric_groups=[(0, 1)],
    ) is None
    assert interaction.get(
        "psi", "chloride-ion|potassium-ion|sodium-ion"
    ) is None
    assert interaction.get(
        "psi",
        "sodium-ion|potassium-ion|chloride-ion",
        symmetric_groups=[(0, 1)],
    ) == 0.0
    assert interaction.get(
        "psi",
        "sodium-ion|chloride-ion|potassium-ion",
        symmetric_groups=[(1, 2)],
    ) == 0.0


def test_interaction_rules_rename_symbols_and_aggregate_metadata():
    _, interaction_thermodb = _build_interaction_thermodb()
    rules = {
        "ALL": {
            "DATA": {
                "psi": "psi_ternary",
                "zeta": "zeta_ternary",
            }
        }
    }

    source = build_interaction_model_source(
        interaction_thermodb,
        rules=rules,
        overwrite_rules=True,
    )
    model_source = build_model_source([source])
    mixture_id = "chloride-ion|potassium-ion|sodium-ion"

    assert set(model_source.data_source[mixture_id]) == {
        "psi_ternary",
        "zeta_ternary",
    }
    assert model_source.data_symbols[mixture_id]["psi_ternary"] == {
        "name": "Pitzer interaction parameters",
        "symbol": "psi_ternary",
        "unit": 1,
    }
    assert model_source.data_symbols[mixture_id]["zeta_ternary"] == {
        "name": "Pitzer interaction parameters",
        "symbol": "zeta_ternary",
        "unit": "mol/kg",
    }


def test_build_interaction_model_source_is_public():
    assert (
        pyThermoLinkDB.build_interaction_model_source
        is build_interaction_model_source
    )


def test_build_model_source_merges_shared_ids_and_mixed_source_types():
    component = Component(name="water", formula="H2O", state="l")
    first_equation = StubTableEquation("first")
    original_collision = StubTableEquation("original")
    second_equation = StubTableEquation("second")
    replacement_collision = StubTableEquation("replacement")

    component_source = ComponentModelSource(
        component=component,
        data_source={
            "water": {
                "first": {
                    "name": "First property",
                    "symbol": "first",
                    "unit": "1",
                    "value": 1,
                },
                "collision": {
                    "name": "Original property",
                    "symbol": "collision",
                    "unit": "1",
                    "value": 10,
                },
            }
        },
        equation_source={
            "water": {
                "first_equation": first_equation,
                "collision": original_collision,
            }
        },
    )
    mixture_source = MixtureModelSource(
        components=[component],
        data_source={
            "water": {
                "second": {
                    "name": "Second property",
                    "symbol": "second",
                    "unit": "K",
                    "value": 2,
                },
                "collision": {
                    "name": "Replacement property",
                    "symbol": "collision",
                    "unit": "mol",
                    "value": 20,
                },
            }
        },
        equation_source={
            "water": {
                "second_equation": second_equation,
                "collision": replacement_collision,
            }
        },
    )
    first_constants = ConstantsModelSource(
        constants_source={
            "R": {
                "name": "Original constant",
                "symbol": "R",
                "unit": "old-unit",
                "value": 1,
            }
        }
    )
    second_constants = ConstantsModelSource(
        constants_source={
            "R": {
                "name": "Replacement constant",
                "symbol": "R",
                "unit": "new-unit",
                "value": 2,
            },
            "g": {
                "name": "Gravity",
                "symbol": "g",
                "unit": "m/s2",
                "value": 9.81,
            },
        }
    )

    model_source = build_model_source([
        component_source,
        first_constants,
        mixture_source,
        second_constants,
    ])

    assert set(model_source.data_source["water"]) == {
        "first",
        "second",
        "collision",
    }
    assert model_source.data_source["water"]["collision"]["value"] == 20
    assert set(model_source.equation_source["water"]) == {
        "first_equation",
        "second_equation",
        "collision",
    }
    assert (
        model_source.equation_source["water"]["first_equation"]
        is first_equation
    )
    assert (
        model_source.equation_source["water"]["second_equation"]
        is second_equation
    )
    assert (
        model_source.equation_source["water"]["collision"]
        is replacement_collision
    )
    assert model_source.constants_source["R"]["value"] == 2
    assert model_source.constants_source["g"]["value"] == 9.81
    assert model_source.data_symbols["water"]["collision"] == {
        "name": "Replacement property",
        "symbol": "collision",
        "unit": "mol",
    }
    assert model_source.constants_symbols["R"] == {
        "name": "Replacement constant",
        "symbol": "R",
        "unit": "new-unit",
    }
