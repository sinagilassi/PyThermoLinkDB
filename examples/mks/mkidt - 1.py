"""Build and query one interaction table with ``mkidt``."""

# SECTION: Direct-script path setup
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# SECTION: Imports
from examples.mks.interaction_data_setup import (  # noqa: E402
    build_example_model_source,
    potassium_components,
)
from pyThermoLinkDB import InteractionDataSourceCore, mkidt  # noqa: E402


# SECTION: Model source
model_source = build_example_model_source()


# SECTION: Build one registered interaction source
interaction_source: InteractionDataSourceCore | None = mkidt(
    name='psi',
    components=potassium_components,
    model_source=model_source,
    mixture_key='Name',
)

# ! Makers return None when validation or construction fails.
if interaction_source is None:
    raise RuntimeError('Failed to create the psi interaction data source.')


# SECTION: Registration metadata
print('Resolved datasource mixture:', interaction_source.mixture_name)
print('Registered interaction keys:', interaction_source.props)
print('Table interaction symbols:', interaction_source.props_symbols)
print('Build summary:', interaction_source.summary())

# NOTE: The outer datasource id is canonicalized alphabetically.
assert interaction_source.mixture_name == (
    'chloride-ion|potassium-ion|sodium-ion'
)


# SECTION: Raw table inspection
print('\nInteraction table:')
print(interaction_source.table(mode='all'))

print('\nInteraction structure:')
print(interaction_source.structure())

print('\nInteraction info:')
print(interaction_source.info())


# SECTION: Ordered scalar lookup
stored_order = 'potassium-ion|sodium-ion|chloride-ion'
different_order = 'sodium-ion|chloride-ion|potassium-ion'

print('\npsi in the stored order:')
print(interaction_source.get('psi', stored_order))

# ! Interaction record order is significant; no implicit sorting occurs.
print('\npsi for a different order without symmetry:')
print(interaction_source.get('psi', different_order))

# ? Explicit symmetry permits permutations only in declared positions.
print('\npsi for the different order with positions 1 and 2 symmetric:')
print(interaction_source.get(
    'psi',
    different_order,
    symmetric_groups=[(1, 2)],
))


# SECTION: DataResult-compatible lookup
print('\nInteraction result mapping:')
print(interaction_source.interaction_i(
    property='psi',
    mixture=stored_order,
    message='Pitzer psi interaction parameter.',
))

print('\nScalar extracted from the result mapping:')
print(interaction_source.interaction_value(
    property='psi',
    mixture=stored_order,
))


# SECTION: Component-object lookup
# NOTE: This ordered component list matches the stored interaction record.
ordered_components = [
    potassium_components[1],
    potassium_components[0],
    potassium_components[2],
]
print('\npsi resolved from Component objects:')
print(interaction_source.get_from_components(
    property_name='psi',
    components=ordered_components,
    component_key='Name',
))
