"""Shared interaction-data setup for the ``mkidt*`` examples."""

# SECTION: Imports
from pyThermoDB import (
    MixtureThermoDB,
    build_interaction_thermodb_from_reference,
)
from pythermodb_settings.models import Component

from pyThermoLinkDB import (
    build_interaction_model_source,
    build_model_source,
)
from pyThermoLinkDB.models import MixtureModelSource, ModelSource


# SECTION: Components
sodium = Component(name='sodium-ion', formula='Na{+}', state='aq')
potassium = Component(name='potassium-ion', formula='K{+}', state='aq')
lithium = Component(name='lithium-ion', formula='Li{+}', state='aq')
chloride = Component(name='chloride-ion', formula='Cl{-}', state='aq')

potassium_components = [sodium, potassium, chloride]
lithium_components = [sodium, lithium, chloride]


# SECTION: Ordered interaction references
# ! The Mixture values below are ordered interaction records. Their member
# ! order must not be canonicalized by PyThermoLinkDB lookup helpers.
POTASSIUM_REFERENCE = """
REFERENCES:
  PITZER-POTASSIUM-EXAMPLE:
    DATABOOK-ID: 1
    TABLES:
      Pitzer potassium interaction parameters:
        TABLE-ID: 1
        DESCRIPTION: Scalar parameters for ordered ternary interactions.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [null, null, psi, zeta]
          UNIT: [null, null, 1, mol/kg]
        VALUES:
          - [1, "potassium-ion|sodium-ion|chloride-ion", -0.0018, 0.25]
          - [2, "sodium-ion|potassium-ion|chloride-ion", 0.0, null]
"""


LITHIUM_REFERENCE = """
REFERENCES:
  PITZER-LITHIUM-EXAMPLE:
    DATABOOK-ID: 1
    TABLES:
      Pitzer lithium interaction parameters:
        TABLE-ID: 1
        DESCRIPTION: Scalar parameters for ordered ternary interactions.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [null, null, psi, zeta]
          UNIT: [null, null, 1, mol/kg]
        VALUES:
          - [1, "lithium-ion|sodium-ion|chloride-ion", -0.0007, 0.12]
          - [2, "sodium-ion|lithium-ion|chloride-ion", 0.0002, null]
"""


# SECTION: ThermoDB builders
def build_interaction_fragment(
    components: list[Component],
    reference_content: str,
) -> MixtureModelSource:
    """Build and validate one interaction model-source fragment."""
    interaction_thermodb: MixtureThermoDB | None = (
        build_interaction_thermodb_from_reference(
            components=components,
            reference_content=reference_content,
            component_key='Name',
        )
    )

    # ! Builder failure must be handled before accessing .thermodb.
    if interaction_thermodb is None:
        raise RuntimeError('Failed to build the interaction ThermoDB.')

    # ! Every reference-built ThermoDB is validated before example use.
    if not interaction_thermodb.thermodb.check():
        raise RuntimeError('The interaction ThermoDB failed validation.')

    return build_interaction_model_source(
        interaction_thermodb=interaction_thermodb,
    )


def build_example_model_source() -> ModelSource:
    """Build one model source containing two interaction mixtures."""
    potassium_source = build_interaction_fragment(
        components=potassium_components,
        reference_content=POTASSIUM_REFERENCE,
    )
    lithium_source = build_interaction_fragment(
        components=lithium_components,
        reference_content=LITHIUM_REFERENCE,
    )

    # NOTE: build_model_source merges the two canonical mixture registrations.
    return build_model_source(
        source=[potassium_source, lithium_source],
    )
