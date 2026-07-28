import os
import sys

# NOTE: allow running this file directly from examples/mks
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pyThermoDB as ptdb
import pyThermoLinkDB as ptdblink
from pyThermoDB import MixtureThermoDB, build_mixture_thermodb_from_reference
from pythermodb_settings.models import Component
from rich import print

from pyThermoLinkDB import (  # noqa: E402
    MatrixDataSourceCore,
    build_mixture_model_source,
    build_model_source,
    mkmdt,
)
from pyThermoLinkDB.models import MixtureModelSource, ModelSource  # noqa: E402


REFERENCE_CONTENT = """
REFERENCES:
    CUSTOM-REF-BINARY:
      DATABOOK-ID: 1
      TABLES:
        NRTL Non-randomness parameters-binary:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides NRTL matrix parameters for methanol and ethanol.
          MATRIX-SYMBOL:
            - a constant: a
            - b constant: b
            - c constant: c
            - non-randomness parameter: alpha
          STRUCTURE:
            COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
"""


def build_binary_model_source(components: list[Component]) -> ModelSource:
    mixture_thermodb: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
        components=components,
        reference_content=REFERENCE_CONTENT,
        component_key='Name-State',
        mixture_key='Name',
    )

    if mixture_thermodb is None:
        raise ValueError("mixture_thermodb is None")

    mixture_model_source: MixtureModelSource = build_mixture_model_source(
        mixture_thermodb=mixture_thermodb,
        mixture_key='Name',
    )

    return build_model_source(
        source=[mixture_model_source],
    )


def show_matrix_access(
    title: str,
    components: list[Component],
    model_source: ModelSource,
) -> None:
    print(f"\n[bold cyan]{title}[/bold cyan]")
    print(f"Component definition order: {[component.name for component in components]}")

    matrix_data_source: MatrixDataSourceCore | None = mkmdt(
        components=components,
        model_source=model_source,
        mixture_key='Name',
        extract_list=['alpha', 'b'],
    )

    if matrix_data_source is None:
        raise ValueError("Failed to create matrix data source.")

    print(f"Resolved mixture name: {matrix_data_source.mixture_name}")

    print("\nSelected alpha table:")
    print(matrix_data_source.table(name='alpha', mode='selected'))

    print("\nMatrix structure:")
    print(matrix_data_source.structure(name='alpha'))

    print("\nAccess alpha_i_j using property string:")
    print("alpha | methanol | ethanol")
    print(matrix_data_source.ij(
        name='alpha',
        property='alpha | methanol | ethanol',
    ))

    print("alpha | ethanol | methanol")
    print(matrix_data_source.ij(
        name='alpha',
        property='alpha | ethanol | methanol',
    ))

    print("\nAccess alpha_i_j using matrix_property:")
    print("component_names=['methanol', 'ethanol']")
    print(matrix_data_source.matrix_property(
        name='alpha',
        property='alpha_i_j',
        component_names=['methanol', 'ethanol'],
    ))

    print("component_names=['ethanol', 'methanol']")
    print(matrix_data_source.matrix_property(
        name='alpha',
        property='alpha_i_j',
        component_names=['ethanol', 'methanol'],
    ))

    print("\nDirectional b_i_j values:")
    print("b | methanol | ethanol")
    print(matrix_data_source.ij(
        name='b',
        property='b | methanol | ethanol',
    ))

    print("b | ethanol | methanol")
    print(matrix_data_source.ij(
        name='b',
        property='b | ethanol | methanol',
    ))

    b_data = matrix_data_source.prop(name='b')

    if b_data is None:
        raise ValueError("Missing b matrix data.")

    component_names = [
        component.name
        for component in components
    ]

    b_matrix = b_data.mat(
        property_name='b',
        component_names=component_names,
        symbol_format='numeric',
        component_key='Name',
    )

    print("\nNumeric b matrix from mat() using component_names order:")
    print(b_matrix)

    if isinstance(b_matrix, np.ndarray):
        print(f"mat() b matrix shape: {b_matrix.shape}")

    b_matrix_x = b_data.matX(
        property_name='b',
        components=components,
        symbol_format='numeric',
        component_key='Name',
    )

    print("\nNumeric b matrix from matX() using the supplied component order:")
    print(b_matrix_x)

    if isinstance(b_matrix_x, np.ndarray):
        print(f"matX() b matrix shape: {b_matrix_x.shape}")


# =======================================
# COMPONENTS
# =======================================
methanol = Component(
    name='methanol',
    formula='CH3OH',
    state='l',
)

ethanol = Component(
    name='ethanol',
    formula='C2H5OH',
    state='l',
)

# version
print(ptdblink.__version__)
print(ptdb.__version__)

# =======================================
# MODEL SOURCE
# =======================================
component_order_1 = [methanol, ethanol]
model_source = build_binary_model_source(components=component_order_1)

# =======================================
# MATRIX ACCESS: ORIGINAL ORDER
# =======================================
show_matrix_access(
    title='Order 1: methanol, ethanol',
    components=component_order_1,
    model_source=model_source,
)

# =======================================
# MATRIX ACCESS: REVERSED ORDER
# =======================================
component_order_2 = [ethanol, methanol]
show_matrix_access(
    title='Order 2: ethanol, methanol',
    components=component_order_2,
    model_source=model_source,
)
