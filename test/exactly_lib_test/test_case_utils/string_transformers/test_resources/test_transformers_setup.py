from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerPrimitiveSymbolContext

DELETE_EVERYTHING_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'DELETE_EVERYTHING_TRANSFORMER',
    string_transformers.delete_everything()
)

DUPLICATE_WORDS_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'DUPLICATE_WORDS_TRANSFORMER',
    string_transformers.duplicate_words()
)

DELETE_INITIAL_WORD_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'DELETE_INITIAL_WORD_TRANSFORMER',
    string_transformers.delete_initial_word()
)

TO_UPPER_CASE_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'TO_UPPER_CASE_TRANSFORMER',
    string_transformers.to_uppercase()
)

SYMBOL_TABLE = SymbolContext.symbol_table_of_contexts([

    DELETE_EVERYTHING_TRANSFORMER,

    DUPLICATE_WORDS_TRANSFORMER,

    DELETE_INITIAL_WORD_TRANSFORMER,

    TO_UPPER_CASE_TRANSFORMER,
])
