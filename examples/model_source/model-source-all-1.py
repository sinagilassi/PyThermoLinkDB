"""Build one ModelSource from every supported pyThermoDB table type.

The example covers TableData, TableEquation, TableMatrixData, and
TableInteractionData (the concrete interaction-table class).
"""

from __future__ import annotations

import sys
from pathlib import Path

from rich import print

# Prefer this checkout when this file is executed directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pyThermoDB import (
    ComponentThermoDB,
    MixtureThermoDB,
    build_component_thermodb_from_reference,
    build_interaction_thermodb_from_reference,
    build_mixture_thermodb_from_reference,
)
from pyThermoDB.core import (
    TableData,
    TableEquation,
    TableInteractionData,
    TableMatrixData,
)
from pythermodb_settings.models import Component
from pyThermoLinkDB.app import (
    build_component_model_source,
    build_interaction_model_source,
    build_mixture_model_source,
    build_model_source,
)
from pyThermoLinkDB.models import ModelSource


# One reference can supply component data/equations, a binary matrix table,
# and ordered scalar interaction data to their corresponding builders.
REFERENCE_CONTENT = """
REFERENCES:
  ALL-TABLES-EXAMPLE:
    DATABOOK-ID: 1
    TABLES:
      general-data:
        TABLE-ID: 1
        DESCRIPTION: Scalar component properties.
        DATA: []
        STRUCTURE:
          COLUMNS: [No., Name, Formula, State, Molecular-Weight, Critical-Temperature]
          SYMBOL: [None, None, None, None, MW, Tc]
          UNIT: [None, None, None, None, g/mol, K]
          CONVERSION: [None, None, None, None, 1, 1]
        VALUES:
          - [1, carbon dioxide, CO2, g, 44.01, 304.21]

      ideal-gas-heat-capacity:
        TABLE-ID: 2
        DESCRIPTION: Linear ideal-gas heat-capacity correlation.
        EQUATIONS:
          EQ-1:
            BODY:
              - res['ideal-gas-heat-capacity | Cp_IG | J/mol.K'] = parms['intercept | a | J/mol.K'] + parms['slope | b | J/mol.K2']*args['temperature | T | K']
            BODY-INTEGRAL: null
            BODY-FIRST-DERIVATIVE: null
            BODY-SECOND-DERIVATIVE: null
        STRUCTURE:
          COLUMNS: [No., Name, Formula, State, intercept, slope, Eq]
          SYMBOL: [None, None, None, None, a, b, Cp_IG]
          UNIT: [None, None, None, None, J/mol.K, J/mol.K2, J/mol.K]
        VALUES:
          - [1, carbon dioxide, CO2, g, 20.0, 0.05, 1]

      binary-matrix-parameters:
        TABLE-ID: 3
        DESCRIPTION: Ordered binary matrix parameters.
        MATRIX-SYMBOL: [tau]
        STRUCTURE:
          COLUMNS: [No., Mixture, Name, Formula, State, tau_i_1, tau_i_2]
          SYMBOL: [None, None, None, None, None, tau_i_1, tau_i_2]
          UNIT: [None, None, None, None, None, 1, 1]
        VALUES:
          - [1, methanol|ethanol, methanol, CH3OH, l, 0.0, 0.30]
          - [2, methanol|ethanol, ethanol, C2H5OH, l, 0.40, 0.0]

      ternary-interaction-parameters:
        TABLE-ID: 4
        DESCRIPTION: Ordered ternary scalar interaction parameters.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [None, None, psi, zeta]
          UNIT: [None, None, 1, mol/kg]
        VALUES:
          - [1, potassium-ion|sodium-ion|chloride-ion, -0.0018, 0.25]
"""


# SECTION: define the component sets used by each table family
carbon_dioxide = Component(name="carbon dioxide", formula="CO2", state="g")

methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
matrix_components = [methanol, ethanol]

sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
interaction_components = [sodium, potassium, chloride]


# SECTION: build and validate the three ThermoDB containers
component_thermodb: ComponentThermoDB | None = (
    build_component_thermodb_from_reference(
        component_name=carbon_dioxide.name,
        component_formula=carbon_dioxide.formula,
        component_state=carbon_dioxide.state,
        reference_content=REFERENCE_CONTENT,
    )
)
if component_thermodb is None or not component_thermodb.thermodb.check():
    raise RuntimeError("The component ThermoDB could not be built.")

matrix_thermodb: MixtureThermoDB | None = (
    build_mixture_thermodb_from_reference(
        components=matrix_components,
        reference_content=REFERENCE_CONTENT,
        component_key="Name-State",
        mixture_key="Name",
    )
)
if matrix_thermodb is None or not matrix_thermodb.thermodb.check():
    raise RuntimeError("The matrix ThermoDB could not be built.")

interaction_thermodb: MixtureThermoDB | None = (
    build_interaction_thermodb_from_reference(
        components=interaction_components,
        reference_content=REFERENCE_CONTENT,
        component_key="Name",
    )
)
if interaction_thermodb is None or not interaction_thermodb.thermodb.check():
    raise RuntimeError("The interaction ThermoDB could not be built.")


# SECTION: select and validate every concrete table type
table_data = component_thermodb.thermodb.select_property(
    "ALL-TABLES-EXAMPLE::general-data"
)
table_equation = component_thermodb.thermodb.select_function(
    "ALL-TABLES-EXAMPLE::ideal-gas-heat-capacity"
)
table_matrix_data = matrix_thermodb.thermodb.select_property(
    "ALL-TABLES-EXAMPLE::binary-matrix-parameters"
)
table_interaction_data = interaction_thermodb.thermodb.select_property(
    "ALL-TABLES-EXAMPLE::ternary-interaction-parameters"
)

if not isinstance(table_data, TableData):
    raise TypeError(f"Expected TableData, got {type(table_data).__name__}.")
if not isinstance(table_equation, TableEquation):
    raise TypeError(
        f"Expected TableEquation, got {type(table_equation).__name__}."
    )
if not isinstance(table_matrix_data, TableMatrixData):
    raise TypeError(
        f"Expected TableMatrixData, got {type(table_matrix_data).__name__}."
    )
if not isinstance(table_interaction_data, TableInteractionData):
    raise TypeError(
        "Expected TableInteractionData, got "
        f"{type(table_interaction_data).__name__}."
    )

raw_tables = (
    table_data,
    table_equation,
    table_matrix_data,
    table_interaction_data,
)


# SECTION: build each specialized source, then aggregate one final ModelSource
component_model_source = build_component_model_source(component_thermodb)
matrix_model_source = build_mixture_model_source(matrix_thermodb)
interaction_model_source = build_interaction_model_source(
    interaction_thermodb
)

model_source: ModelSource = build_model_source(
    source=[
        component_model_source,
        matrix_model_source,
        interaction_model_source,
    ]
)


# SECTION: access each table through its appropriate representation
component_id = "carbon dioxide-g"
matrix_id = "ethanol|methanol"
interaction_id = "chloride-ion|potassium-ion|sodium-ion"

# TableData is deliberately normalized to individual property dictionaries in
# a ModelSource. The raw TableData remains available from component_thermodb.
mw_property = model_source.data_source[component_id]["MW"]
equation_from_model = model_source.equation_source[component_id]["Cp_IG"]
matrix_from_model = model_source.data_source[matrix_id]["tau"]
interaction_from_model = model_source.data_source[interaction_id]["psi"]

if not isinstance(mw_property, dict):
    raise TypeError("Expected normalized TableData property metadata.")
if not isinstance(equation_from_model, TableEquation):
    raise TypeError("Expected TableEquation in the final ModelSource.")
if not isinstance(matrix_from_model, TableMatrixData):
    raise TypeError("Expected TableMatrixData in the final ModelSource.")
if not isinstance(interaction_from_model, TableInteractionData):
    raise TypeError("Expected TableInteractionData in the final ModelSource.")


print("Available raw table types:")
for table in raw_tables:
    print(f"  {type(table).__name__}: {table.table_name}")

print("\nFinal ModelSource data IDs:", list(model_source.data_source))
print("Final ModelSource equation IDs:", list(model_source.equation_source))
print("Molecular weight property:", mw_property)
print("Cp_IG at 300 K:", equation_from_model.cal(T=300.0))
print(
    "tau matrix:",
    matrix_from_model.mat("tau", ["methanol", "ethanol"]),
)
print(
    "psi interaction:",
    interaction_from_model.get(
        "psi",
        "potassium-ion|sodium-ion|chloride-ion",
    ),
)
