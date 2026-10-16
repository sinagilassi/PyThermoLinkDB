"""Build a reusable model source for scalar interaction data."""

from __future__ import annotations
from pyThermoLinkDB.app import (
    build_interaction_model_source,
    build_model_source,
)
from pythermodb_settings.models import Component
from pyThermoDB import (
    MixtureThermoDB,
    TableInteractionData,
    build_interaction_thermodb_from_reference,
)
from typing import Dict, Any
from pyThermoLinkDB.models import DataSource

import sys
from pathlib import Path

from rich import print

# Prefer this checkout when this file is executed directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# SECTION: interaction reference used to build the saved ThermoDB source
REFERENCE_CONTENT = """
REFERENCES:
  PITZER-MODEL-SOURCE:
    DATABOOK-ID: 1
    TABLES:
      Pitzer interaction parameters:
        TABLE-ID: 1
        DESCRIPTION:
          Scalar interaction parameters for an ordered ternary mixture.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [None, None, psi, zeta]
          UNIT: [None, None, 1, 1]
        VALUES:
          - [1, "potassium-ion|sodium-ion|chloride-ion", -0.0018, 0.25]
"""


# SECTION: components represented by the interaction model source
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]


# SECTION: build and save the ThermoDB used by the model source
EXAMPLE_DIR = Path(__file__).resolve().parent
THERMODB_DIR = EXAMPLE_DIR / "thermodb"
THERMODB_NAME = "pitzer-interaction-model-source"
THERMODB_PATH = THERMODB_DIR / f"{THERMODB_NAME}.pkl"

built: MixtureThermoDB | None = build_interaction_thermodb_from_reference(
    components=components,
    reference_content=REFERENCE_CONTENT,
    component_key="Name",
    thermodb_name=THERMODB_NAME,
    message="Pitzer interaction data for a reusable model source.",
    thermodb_save=True,
    thermodb_save_path=str(THERMODB_DIR),
)
if built is None:
    raise RuntimeError("No matching interaction-data ThermoDB was built.")

if not built.thermodb.check():
    raise RuntimeError("The interaction ThermoDB failed validation.")
if not THERMODB_PATH.is_file():
    raise FileNotFoundError(f"Saved ThermoDB was not found: {THERMODB_PATH}")


# SECTION: build the interaction model source
interaction_model_source = build_interaction_model_source(
    interaction_thermodb=built,
)
model_source = build_model_source(
    source=[interaction_model_source],
)

print("Interaction model source:", interaction_model_source)
print("Combined model source:", model_source)
print("Data-source mixtures:", list(model_source.data_source))


# SECTION: prove that the model source preserves the queryable interaction table
model_mixture = "chloride-ion|potassium-ion|sodium-ion"

# interaction data
interaction_data: Dict[str, Any] = model_source.data_source[model_mixture]

# phi
phi_src = interaction_data["psi"]
if not isinstance(phi_src, TableInteractionData):
    raise TypeError("Expected TableInteractionData from the model source.")

source_mixture = "potassium-ion|sodium-ion|chloride-ion"
request_mixture = "sodium-ion|potassium-ion|chloride-ion"

print("Stored mixtures:", phi_src.mixtures)
print("psi in source order:", phi_src.get("psi", source_mixture))
print("psi in request order (strict):",
      phi_src.get("psi", request_mixture))
print(
    "psi in request order (first two positions symmetric):",
    phi_src.get(
        "psi",
        request_mixture,
        symmetric_groups=[(0, 1)],
    ),
)
