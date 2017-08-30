from exactly_lib.default.program_modes.test_case import predef_symbols
from exactly_lib.execution import full_execution
from exactly_lib.util.symbol_table import symbol_table_with_entries

PREDEFINED_PROPERTIES = full_execution.PredefinedProperties(
    predefined_symbols=symbol_table_with_entries(predef_symbols.ALL)
)
