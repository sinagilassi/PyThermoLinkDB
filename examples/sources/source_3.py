"""Use ``Source`` with scalar ``TableInteractionData`` entries."""

from __future__ import annotations
from pyThermoLinkDB.thermo import Source
from pyThermoLinkDB import (
    build_interaction_model_source,
    build_model_source,
)
from pythermodb_settings.models import Component
from pyThermoDB import (
    MixtureThermoDB,
    TableInteractionData,
    build_interaction_thermodb_from_reference,
)
import pyThermoLinkDB as ptdblink
import pyThermoDB as ptdb

import sys
from pathlib import Path

from rich import print

# Prefer this checkout when the example is executed directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ====================================================
# SECTION: INTERACTION REFERENCE CONTENT
# ====================================================
REFERENCE_CONTENT = """
REFERENCES:
  PITZER-SOURCE-EXAMPLE:
    DATABOOK-ID: 1
    TABLES:
      Pitzer interaction parameters:
        TABLE-ID: 1
        DESCRIPTION:
          Scalar parameters for ordered ternary interactions.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [None, None, psi, zeta]
          UNIT: [None, None, 1, mol/kg]
        VALUES:
          - [1, "potassium-ion|sodium-ion|chloride-ion", -0.0018, 0.25]
          - [2, "sodium-ion|potassium-ion|chloride-ion", 0.0, null]
"""


# ====================================================
# SECTION: COMPONENTS
# ====================================================
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]


def main() -> None:
    """Build an interaction source and exercise the ``Source`` helpers."""
    print("pyThermoDB:", ptdb.__version__)
    print("pyThermoLinkDB:", ptdblink.__version__)

    # ====================================================
    # SECTION: BUILD INTERACTION THERMODB
    # ====================================================
    interaction_thermodb: MixtureThermoDB | None = (
        build_interaction_thermodb_from_reference(
            components=components,
            reference_content=REFERENCE_CONTENT,
            component_key="Name",
        )
    )
    if interaction_thermodb is None:
        raise RuntimeError("No interaction ThermoDB was built.")
    if not interaction_thermodb.thermodb.check():
        raise RuntimeError("The interaction ThermoDB failed validation.")

    # The rules argument is optional. When omitted, the model-source builder
    # uses the rules already stored in the interaction ThermoDB metadata.
    interaction_model_source = build_interaction_model_source(
        interaction_thermodb=interaction_thermodb,
    )
    model_source = build_model_source(source=[interaction_model_source])

    # ====================================================
    # SECTION: MAKE SOURCE
    # ====================================================
    source = Source(
        model_source=model_source,
        mixture_key="Name",
    )

    # Model-source registration ids are canonicalized alphabetically.
    registered_mixture = "chloride-ion|potassium-ion|sodium-ion"
    unordered_registration_id = "sodium-ion|chloride-ion|potassium-ion"

    # Interaction record order remains significant and is never sorted.
    stored_query = "psi | potassium-ion|sodium-ion|chloride-ion"
    symmetric_query = "psi | sodium-ion|chloride-ion|potassium-ion"

    # ====================================================
    # SECTION: TABLE INTERACTION DATA ACCESS
    # ====================================================
    interaction_data = source.get_interaction(
        mixture_name=unordered_registration_id,
        prop_name="psi",
    )
    if not isinstance(interaction_data, TableInteractionData):
        raise TypeError(
            "Expected TableInteractionData for the registered psi property."
        )

    print("Registered datasource symbols:")
    print(source.data_symbols[registered_mixture])

    print("Interaction symbols:")
    print(interaction_data.interaction_symbol)

    print("Stored ordered mixtures:")
    print(interaction_data.mixtures)

    print("Interaction table:")
    print(interaction_data.get_interaction_table(mode="all"))

    # prop_name locates the datasource table. property is the compact
    # query that identifies the symbol and exact ordered interaction record.
    print("psi scalar in source order:")
    print(source.interaction_value(
        mixture_name=registered_mixture,
        prop_name="psi",
        property=stored_query,
    ))

    print("psi scalar for a missing order (strict):")
    print(source.interaction_value(
        mixture_name=registered_mixture,
        prop_name="psi",
        property=symmetric_query,
    ))

    print("psi scalar using explicit symmetry for positions 1 and 2:")
    print(source.interaction_value(
        mixture_name=registered_mixture,
        prop_name="psi",
        property=symmetric_query,
        symmetric_groups=[(1, 2)],
    ))

    print("psi as a DataResult-style mapping:")
    print(source.interaction_i(
        mixture_name=registered_mixture,
        prop_name="psi",
        property=stored_query,
        message="Pitzer psi interaction parameter.",
    ))

    print("All psi values by ordered mixture:")
    print(source.interaction_property(
        mixture_name=registered_mixture,
        prop_name="psi",
    ))

    print("All zeta values, including unavailable values:")
    print(source.interaction_property(
        mixture_name=registered_mixture,
        prop_name="zeta",
    ))

    print(source.interaction_property(
        mixture_name=registered_mixture,
        prop_name="zeta",
        include_null=True,
    ))

    # TableInteractionData is also preserved as an equation argument, just as
    # TableMatrixData is.
    interaction_args = source.build_args(
        component_id=registered_mixture,
        args={
            "psi": {
                "symbol": "psi",
                "unit": 1,
            }
        },
    )
    print("Interaction datasource argument:")
    print(interaction_args)


if __name__ == "__main__":
    main()
