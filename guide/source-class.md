# `Source` class

`pyThermoLinkDB.thermo.Source` is the runtime access layer around a
`ModelSource`. It exposes the combined datasource, equationsource, constants
source, symbol metadata, equation builders/evaluators, and matrix-data helpers.

The examples in `examples/sources/source_0.py`, `source_1.py`, and
`source_2.py` demonstrate three main usage paths:

- component equation access and evaluation,
- component datasource and constants access,
- mixture `TableMatrixData` extraction and matrix construction.

## Construction

```python
source = Source(
    model_source=model_source,
    component_key="Formula-State",
    mixture_key="Name",
)
```

`component_key` controls how `Component` objects are mapped into component ids
for equation execution. `mixture_key` controls how `matX()` builds mixture ids
from `Component` objects.

Supported component keys:

- `Name-State`
- `Formula-State`
- `Name-Formula`
- `Name-Formula-State`
- `Formula-Name-State`

Supported mixture keys:

- `Name`
- `Formula`

## Source Shape

```mermaid
classDiagram
    class ModelSource {
        Dict data_source
        Dict equation_source
        Optional~Dict~ constants_source
        Optional~Dict~ data_symbols
        Optional~Dict~ equation_symbols
        Optional~Dict~ constants_symbols
    }

    class Source {
        ModelSource model_source
        ComponentKey component_key
        MixtureKey mixture_key
        Dict datasource
        Dict equationsource
        Dict constantssource
        Dict datasource_symbols
        Dict equationsource_symbols
        Dict constantssource_symbols
        List component_keys
        set_source(model_source)
    }

    class ComponentEquationSource {
        TableEquation source
        Dict inputs
        int num
        Callable fn
        str body
        Dict args
        Dict arg_symbols
        List arg_identifiers
        Dict arg_mappings
        Dict returns
        Dict return_symbols
        List return_identifiers
    }

    class TableEquation {
        Dict args
        Dict arg_symbols
        Dict returns
        Dict return_symbols
        int eq_num
        str body
        cal()
        make_identifiers()
    }

    class TableMatrixData {
        Dict matrix_symbol
        matrix_data_structure()
        get_matrix_table()
        ij()
        get_matrix_property()
        mat()
        matX()
    }

    ModelSource --> Source : passed to constructor
    Source --> ComponentEquationSource : eq_builder()
    ComponentEquationSource --> TableEquation : wraps
    Source --> TableMatrixData : get_matrix()
```

## Public API Groups

```mermaid
classDiagram
    class Source {
        +datasource
        +equationsource
        +constantssource
        +datasource_symbols
        +equationsource_symbols
        +constantssource_symbols
        +data_symbols
        +equation_symbols
        +constants_symbols

        +eq_extractor(component_id, prop_name)
        +eq_symbol(component_id, prop_name)
        +component_eq_extractor(component_id)
        +component_eq_symbols(component_id)
        +eq_builder(components, prop_name, component_key, component_keys)
        +exec_eq(components, eq_src_comp, args_values)
        +eval_eq(components, eq_src_comp, args_values)
        +eq_eval(components, eq_src_comp, args_values)

        +data_extractor(component_id, prop_name)
        +data_symbol(component_id, prop_name)
        +get_prop(component_id, prop_name)
        +get_prop_symbol(component_id, prop_name)
        +component_data_extractor(component_id)
        +component_data_symbols(component_id)
        +get_dt(component_id)
        +get_dt_symbols(component_id)
        +get_component_data(component_id, components, component_key)

        +constants_extractor(constant_name)
        +constant_symbol(constant_name)
        +const(constant_name)
        +const_symbol(constant_name)

        +matrix_data_extractor(mixture_name, prop_name)
        +get_matrix(mixture_name, prop_name)
        +matrix_ij(mixture_name, prop_name, property)
        +matrix_property(mixture_name, prop_name, property, component_names)
        +mat(mixture_name, prop_name, symbol_format, component_key)
        +matX(prop_name, components, symbol_format, component_key, mixture_key)

        +check_args(component_id, args)
        +build_args(component_id, args, ignore_symbols)
        +is_prop_available(component_id, prop_name)
        +is_prop_eq_available(component_id, prop_name)
        +is_prop_data_available(component_id, prop_name)
        +is_constant_available(constant_name)
    }
```

## Initialization Flow

```mermaid
flowchart TD
    A["Source(model_source, component_key, mixture_key)"] --> B{"model_source is None?"}
    B -->|Yes| C["Set datasource, equationsource, constantssource, and symbols to None"]
    B -->|No| D["Read model_source.data_source"]
    B -->|No| E["Read model_source.equation_source"]
    B -->|No| F["Read model_source.constants_source or {}"]
    B -->|No| G["Read data_symbols, equation_symbols, constants_symbols"]
    D --> H["set_source({datasource, equationsource, constantssource})"]
    E --> H
    F --> H
    H --> I["Store internal _datasource, _equationsource, _constantssource"]
    G --> J["Store symbol metadata"]
    C --> K["Properties return {} when internal sources are None"]
    I --> K
    J --> K
```

## Equation Flow

This is the path used in `source_0.py` and `source_1.py`.

```python
eq_src = source.eq_builder(
    components=[CO2],
    prop_name="Cp_IG",
    component_keys=["Name-State", "Formula-State", "Name-Formula-State"],
)

result = source.eq_eval(
    components=[CO2],
    eq_src_comp=eq_src,
    args_values={"T": 298.15},
)
```

```mermaid
flowchart TD
    A["eq_builder(components, prop_name)"] --> B["Map Component objects to ids with component_key"]
    B --> C{"prop_name available in equationsource for each id?"}
    C -->|No| D["Log error and return None"]
    C -->|Yes| E["eq_extractor(component_id, prop_name)"]
    E --> F["Read TableEquation args and metadata"]
    F --> G["check_args(component_id, eq.args)"]
    G --> H["build_args(component_id, arg_mapping)"]
    H --> I["Create ComponentEquationSource"]
    I --> J{"component_keys supplied?"}
    J -->|Yes| K["Add aliases for alternate component ids"]
    J -->|No| L["Return {component_id: ComponentEquationSource}"]
    K --> L

    M["eq_eval()/eval_eq()/exec_eq()"] --> N["Map components with Source.component_key"]
    N --> O["Find each ComponentEquationSource"]
    O --> P["Merge args_values into inputs"]
    P --> Q["Call ComponentEquationSource.fn(**inputs)"]
    Q --> R["Return (values, result_dict)"]
```

Equation result shape:

```python
(
    [value_0, value_1],
    {
        "CO2-g": {
            "property_name": "ideal-gas-heat-capacity",
            "value": value_0,
            "unit": "J/mol.K",
            "symbol": "Cp_IG",
        }
    },
)
```

## Component Data And Symbols

This is the datasource access path used in `source_1.py`.

```python
source.get_dt("CO2-g")
source.get_dt_symbols("CO2-g")
source.get_prop("CO2-g", "EnFo_IG")
source.get_prop_symbol("CO2-g", "EnFo_IG")
```

```mermaid
flowchart TD
    A["get_dt(component_id)"] --> B["component_data_extractor(component_id)"]
    B --> C["Return datasource[component_id] or None"]

    D["get_prop(component_id, prop_name)"] --> E["data_extractor(component_id, prop_name)"]
    E --> F["Return datasource[component_id][prop_name] or None"]

    G["get_dt_symbols(component_id)"] --> H["component_data_symbols(component_id)"]
    H --> I["Return datasource_symbols[component_id] or None"]

    J["get_prop_symbol(component_id, prop_name)"] --> K["data_symbol(component_id, prop_name)"]
    K --> L["Return datasource_symbols[component_id][prop_name] or None"]
```

Typical property-data shape:

```python
{
    "property_name": "enthalpy-of-formation",
    "symbol": "EnFo_IG",
    "unit": "kJ/mol",
    "value": -393.51,
    "message": "No message",
}
```

## Constants

This is the constants path used in `source_1.py`.

```python
source.is_constant_available("R")
source.const("R")
source.const_symbol("R")
```

```mermaid
flowchart TD
    A["is_constant_available(constant_name)"] --> B{"constant_name in constantssource?"}
    B -->|Yes| C["Return True"]
    B -->|No| D["Return False"]

    E["const(constant_name)"] --> F["constants_extractor(constant_name)"]
    F --> G["Return constantssource[constant_name] or None"]

    H["const_symbol(constant_name)"] --> I["constant_symbol(constant_name)"]
    I --> J["Return constantssource_symbols[constant_name] or None"]
```

## Mixture Matrix Data

This is the mixture path used in `source_2.py`. The mixture model source stores
matrix-like properties as `TableMatrixData` entries under a mixture id.

```python
mixture_id = "butyl-methyl-ether|ethanol|methanol"

matrix_data = source.get_matrix(
    mixture_name=mixture_id,
    prop_name="alpha",
)

alpha_ij = source.matrix_ij(
    mixture_name=mixture_id,
    prop_name="alpha",
    property="alpha | methanol | ethanol",
)

alpha_matrix = source.mat(
    mixture_name=mixture_id,
    prop_name="alpha",
    symbol_format="numeric",
)

alpha_matrix_from_components = source.matX(
    prop_name="alpha",
    components=[methanol, ethanol, butyl_methyl_ether],
    symbol_format="alphabetic",
)
```

```mermaid
flowchart TD
    A["get_matrix(mixture_name, prop_name)"] --> B["matrix_data_extractor(mixture_name, prop_name)"]
    B --> C{"mixture_name in datasource?"}
    C -->|No| D["Log error and return None"]
    C -->|Yes| E{"prop_name in datasource[mixture_name]?"}
    E -->|No| D
    E -->|Yes| F{"entry is TableMatrixData?"}
    F -->|No| D
    F -->|Yes| G["Return TableMatrixData"]

    H["matrix_ij(...)"] --> B
    H --> I["TableMatrixData.ij(property, symbol_format, message)"]

    J["matrix_property(...)"] --> B
    J --> K["TableMatrixData.get_matrix_property(property, component_names, symbol_format)"]

    L["mat(mixture_name, prop_name)"] --> M["canonicalize_mixture_name()"]
    M --> B
    L --> N["TableMatrixData.mat(property_name=prop_name, component_names, symbol_format, component_key)"]

    O["matX(prop_name, components)"] --> P["create_mixture_id(components, mixture_key)"]
    P --> B
    O --> Q["TableMatrixData.matX(property_name=prop_name, components, symbol_format, component_key)"]
```

`mat()` starts from a mixture id string and canonicalizes it before lookup.
`matX()` starts from `Component` objects, creates the sorted mixture id with
`create_mixture_id()`, then returns the matrix in the order implied by the
provided components.

## Availability Helpers

```python
source.is_prop_available("CO2-g", "Cp_IG")
source.is_prop_eq_available("CO2-g", "Cp_IG")
source.is_prop_data_available("CO2-g", "EnFo_IG")
source.is_constant_available("R")
```

```mermaid
flowchart TD
    A["is_prop_available(component_id, prop_name)"] --> B{"In equationsource?"}
    B -->|Yes| C["Return True"]
    B -->|No| D{"In datasource?"}
    D -->|Yes| C
    D -->|No| E["Return False"]

    F["is_prop_eq_available(component_id, prop_name)"] --> G{"In equationsource?"}
    G -->|Yes| C
    G -->|No| E

    H["is_prop_data_available(component_id, prop_name)"] --> I{"In datasource?"}
    I -->|Yes| C
    I -->|No| E
```

## End-To-End Example Map

```mermaid
flowchart LR
    A["source_0.py"] --> A1["Build ModelSource from components + constants"]
    A1 --> A2["Source(model_source, component_key='Formula-State')"]
    A2 --> A3["eq_builder([CO2], 'Cp_IG')"]

    B["source_1.py"] --> B1["Read source symbols"]
    B1 --> B2["Build and evaluate Cp_IG equation"]
    B2 --> B3["Read component data and constants"]

    C["source_2.py"] --> C1["Build MixtureModelSource"]
    C1 --> C2["Source(model_source, mixture_key='Name')"]
    C2 --> C3["Extract TableMatrixData"]
    C3 --> C4["Read i,j values and full matrices"]
```
