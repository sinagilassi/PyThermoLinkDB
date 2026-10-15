"""Build and query multiple interaction tables with ``mkidts``."""

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
from pyThermoLinkDB import InteractionDataSourcesCore, mkidts  # noqa: E402


# SECTION: Model source
model_source = build_example_model_source()


# SECTION: Build selected interaction sources
interaction_sources: InteractionDataSourcesCore | None = mkidts(
    components=potassium_components,
    model_source=model_source,
    mixture_key='Name',
    extract_list=['psi', 'zeta'],
)

# ! Makers return None when validation or construction fails.
if interaction_sources is None:
    raise RuntimeError('Failed to create interaction data sources.')


# SECTION: Build metadata
print('Resolved datasource mixture:', interaction_sources.mixture_name)
print('Selected registration keys:', interaction_sources.props)
print('De-duplicated table symbols:', interaction_sources.props_symbols)
print('Build summary:', interaction_sources.summary())
print('Build status:', interaction_sources.build_status())

print('psi available:', interaction_sources.is_prop_available('psi'))
print('unknown available:', interaction_sources.is_prop_available('unknown'))
print('Availability map:', interaction_sources.check_availability([
    'psi',
    'zeta',
    'unknown',
]))


# SECTION: Singular source selection
psi_source = interaction_sources.select('psi')
if psi_source is None:
    raise RuntimeError('The requested psi source was not built.')

print('\nSelected singular source:')
print(psi_source.interaction_data_source)


# SECTION: Name-prefixed lookup facade
stored_order = 'potassium-ion|sodium-ion|chloride-ion'
null_order = 'sodium-ion|potassium-ion|chloride-ion'

print('\npsi scalar:')
print(interaction_sources.get(
    name='psi',
    property_name='psi',
    mixture=stored_order,
))

print('\nzeta scalar:')
print(interaction_sources.get(
    name='zeta',
    property_name='zeta',
    mixture=stored_order,
))


# SECTION: Property aggregation
print('\nAll available psi values:')
print(interaction_sources.interaction_property(
    name='psi',
    property_name='psi',
))

print('\nAvailable zeta values only:')
print(interaction_sources.interaction_property(
    name='zeta',
    property_name='zeta',
))

# ? include_null preserves explicitly unavailable scalar records.
print('\nAll zeta values, including null:')
print(interaction_sources.interaction_property(
    name='zeta',
    property_name='zeta',
    include_null=True,
))

print('\nNull zeta record:')
print(interaction_sources.get_mixture(
    name='zeta',
    mixture=null_order,
    include_null=True,
))


# SECTION: Record filtering
print('\nTernary psi records containing potassium-ion:')
print(interaction_sources.select_records(
    name='psi',
    property_name='psi',
    contains=['potassium-ion'],
    order=3,
))
