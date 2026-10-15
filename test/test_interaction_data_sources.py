import pytest

import pyThermoLinkDB
from pyThermoDB import TableInteractionData
from pyThermoDB.handlers import TableInteractionDataLookupError
from pythermodb_settings.models import Component

from pyThermoLinkDB.models import InteractionDataSource, ModelSource
from pyThermoLinkDB.thermo import (
    InteractionDataSource as ThermoInteractionDataSource,
    InteractionDataSourceCore,
    InteractionDataSourcesCore,
    mkidt,
    mkidts,
    mkidtss,
)


def make_interaction_source():
    sodium = Component(name='sodium-ion', formula='Na{+}', state='aq')
    potassium = Component(name='potassium-ion', formula='K{+}', state='aq')
    chloride = Component(name='chloride-ion', formula='Cl{-}', state='aq')
    components = [sodium, potassium, chloride]
    table = TableInteractionData(
        databook_name='PITZER-EXAMPLE',
        table_name='Pitzer interaction parameters',
        table_data={
            'INTERACTION-SYMBOL': ['psi', 'zeta'],
            'STRUCTURE': {
                'COLUMNS': ['No.', 'Mixture', 'psi', 'zeta'],
                'SYMBOL': [None, None, 'psi', 'zeta'],
                'UNIT': [None, None, 1, 'mol/kg'],
            },
            'VALUES': [
                [
                    1,
                    'potassium-ion|sodium-ion|chloride-ion',
                    -0.0018,
                    0.25,
                ],
                [
                    2,
                    'sodium-ion|potassium-ion|chloride-ion',
                    0.0,
                    None,
                ],
            ],
        },
    )
    mixture_name = 'chloride-ion|potassium-ion|sodium-ion'
    model_source = ModelSource(
        data_source={
            mixture_name: {
                'psi_ternary': table,
                'zeta': table,
                'ordinary': {'value': 1},
            }
        },
        equation_source={mixture_name: {}},
    )
    return components, table, model_source


def test_singular_core_preserves_order_and_registration_alias():
    components, table, model_source = make_interaction_source()
    source = mkidt(
        name='psi_ternary',
        components=components,
        model_source=model_source,
    )

    assert isinstance(source, InteractionDataSourceCore)
    assert source.status is True
    assert source.interaction_source is table
    assert isinstance(source.interaction_data_source, InteractionDataSource)
    assert source.interaction_data_source.prop_name == 'psi_ternary'
    assert source.props == ['psi_ternary', 'zeta']
    assert source.props_symbols == ['psi', 'zeta']

    stored = 'potassium-ion|sodium-ion|chloride-ion'
    reordered = 'sodium-ion|chloride-ion|potassium-ion'
    assert source.get('psi', stored) == -0.0018
    assert source.get('psi', reordered) is None
    assert source.get(
        'psi',
        reordered,
        symmetric_groups=[(1, 2)],
    ) == 0.0
    assert source.interaction_value(
        'psi',
        'sodium-ion|potassium-ion|chloride-ion',
    ) == 0.0


def test_singular_core_facade_and_native_errors():
    components, _, model_source = make_interaction_source()
    source = mkidt('psi_ternary', components, model_source)
    assert source is not None

    stored = 'potassium-ion|sodium-ion|chloride-ion'
    assert source.has('psi', stored)
    assert source.get_mixture(stored) == {'psi': -0.0018, 'zeta': 0.25}
    assert source.get_property('zeta') == {
        ('potassium-ion', 'sodium-ion', 'chloride-ion'): 0.25,
    }
    assert source.interaction_order(stored) == 3
    assert source.i('psi', stored)['value'] == -0.0018
    assert source.table() is not None
    assert source.structure() is not None
    assert source.info()['INTERACTION-SYMBOL'] == ['psi', 'zeta']
    assert source.get_from_components(
        'psi',
        [components[1], components[0], components[2]],
        component_key='Name',
    ) == -0.0018

    with pytest.raises(TableInteractionDataLookupError):
        source.require('psi', 'missing|ordered|mixture')


def test_plural_core_filters_and_deduplicates_shared_table_symbols():
    components, _, model_source = make_interaction_source()
    sources = mkidts(components, model_source)

    assert isinstance(sources, InteractionDataSourcesCore)
    assert sources.props == ['psi_ternary', 'zeta']
    assert sources.props_symbols == ['psi', 'zeta']
    assert isinstance(sources.select('psi_ternary'), InteractionDataSourceCore)
    assert sources.get(
        'psi_ternary',
        'psi',
        'potassium-ion|sodium-ion|chloride-ion',
    ) == -0.0018

    filtered = mkidts(
        components,
        model_source,
        extract_list=['psi_ternary', 'missing'],
    )
    assert filtered is not None
    assert filtered.props == ['psi_ternary']
    assert filtered.summary() == {'psi_ternary': True, 'missing': False}
    assert filtered.build_status() is False


def test_interaction_makers_validation_multiple_and_exports():
    components, _, model_source = make_interaction_source()

    assert mkidt('', components, model_source) is None
    assert mkidts([], model_source) is None
    assert mkidtss([], model_source) is None

    multiple = mkidtss(
        mixture_components=[components],
        model_source=model_source,
        extract_list=['psi_ternary'],
        check_build=True,
    )
    assert multiple is not None
    assert list(multiple) == ['chloride-ion|potassium-ion|sodium-ion']

    assert pyThermoLinkDB.InteractionDataSource is InteractionDataSource
    assert ThermoInteractionDataSource is InteractionDataSource
    assert pyThermoLinkDB.InteractionDataSourceCore is InteractionDataSourceCore
    assert pyThermoLinkDB.InteractionDataSourcesCore is InteractionDataSourcesCore
    assert pyThermoLinkDB.mkidt is mkidt
    assert pyThermoLinkDB.mkidts is mkidts
    assert pyThermoLinkDB.mkidtss is mkidtss
