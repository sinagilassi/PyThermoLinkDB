"""Build interaction sources for multiple mixtures with ``mkidtss``."""

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
    lithium_components,
    potassium_components,
)
from pyThermoLinkDB import InteractionDataSourcesCore, mkidtss  # noqa: E402


# SECTION: Model source
model_source = build_example_model_source()


# SECTION: Build interaction sources for both mixtures
mixture_components = [
    potassium_components,
    lithium_components,
]

interaction_sources_by_mixture: (
    dict[str, InteractionDataSourcesCore] | None
) = mkidtss(
    mixture_components=mixture_components,
    model_source=model_source,
    mixture_key='Name',
    extract_list=['psi', 'zeta'],
    check_build=True,
)

# ! Makers return None when validation or construction fails.
if interaction_sources_by_mixture is None:
    raise RuntimeError('Failed to create interaction sources by mixture.')


# SECTION: Canonical outer mixture keys
print('Canonical datasource mixture ids:')
for mixture_id in interaction_sources_by_mixture:
    print(' -', mixture_id)

potassium_mixture_id = 'chloride-ion|potassium-ion|sodium-ion'
lithium_mixture_id = 'chloride-ion|lithium-ion|sodium-ion'

assert set(interaction_sources_by_mixture) == {
    potassium_mixture_id,
    lithium_mixture_id,
}


# SECTION: Ordered record queries by outer mixture
# NOTE: Each mapping key is canonical, but each query preserves source order.
ordered_queries = {
    potassium_mixture_id: 'potassium-ion|sodium-ion|chloride-ion',
    lithium_mixture_id: 'lithium-ion|sodium-ion|chloride-ion',
}

for mixture_id, ordered_query in ordered_queries.items():
    interaction_sources = interaction_sources_by_mixture[mixture_id]

    print(f'\n=== {mixture_id} ===')
    print('Components:', interaction_sources.component_names)
    print('Properties:', interaction_sources.props)
    print('Symbols:', interaction_sources.props_symbols)
    print('Summary:', interaction_sources.summary())
    print('Status:', interaction_sources.build_status())

    print('Ordered psi value:')
    print(interaction_sources.interaction_value(
        name='psi',
        property='psi',
        mixture=ordered_query,
    ))

    print('Ordered interaction result:')
    print(interaction_sources.interaction_i(
        name='psi',
        property='psi',
        mixture=ordered_query,
        message=f'psi value for {ordered_query}',
    ))


# SECTION: Demonstrate order sensitivity
potassium_sources = interaction_sources_by_mixture[potassium_mixture_id]
different_order = 'sodium-ion|chloride-ion|potassium-ion'

print('\nDifferent potassium interaction order without symmetry:')
print(potassium_sources.interaction_value(
    name='psi',
    property='psi',
    mixture=different_order,
))

# ? Explicit symmetry allows positions 1 and 2 to be interchanged.
print('Different potassium interaction order with explicit symmetry:')
print(potassium_sources.interaction_value(
    name='psi',
    property='psi',
    mixture=different_order,
    symmetric_groups=[(1, 2)],
))
