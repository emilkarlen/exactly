from exactly_lib_test.symbol.test_resources.string_transformer import StringTransformerPrimitiveSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.type_system.logic.string_transformer import test_resources
from exactly_lib_test.type_system.logic.test_resources import string_transformers

DELETE_EVERYTHING_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'DELETE_EVERYTHING_TRANSFORMER',
    test_resources.DeleteEverythingTransformer()
)

DUPLICATE_WORDS_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'DUPLICATE_WORDS_TRANSFORMER',
    string_transformers.DuplicateWordsTransformer()
)

DELETE_INITIAL_WORD_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'DELETE_INITIAL_WORD_TRANSFORMER',
    string_transformers.DeleteInitialWordTransformer()
)

TO_UPPER_CASE_TRANSFORMER = StringTransformerPrimitiveSymbolContext(
    'TO_UPPER_CASE_TRANSFORMER',
    string_transformers.MyToUppercaseTransformer()
)

SYMBOL_TABLE = SymbolContext.symbol_table_of_contexts([

    DELETE_EVERYTHING_TRANSFORMER,

    DUPLICATE_WORDS_TRANSFORMER,

    DELETE_INITIAL_WORD_TRANSFORMER,

    TO_UPPER_CASE_TRANSFORMER,
])
