from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import string_transformer
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.type_system.logic.string_transformer import test_resources
from exactly_lib_test.type_system.logic.test_resources import string_transformers

DELETE_EVERYTHING_TRANSFORMER = NameAndValue('DELETE_EVERYTHING_TRANSFORMER',
                                             test_resources.DeleteEverythingTransformer()
                                             )

DUPLICATE_WORDS_TRANSFORMER = NameAndValue('DUPLICATE_WORDS_TRANSFORMER',
                                           string_transformers.DuplicateWordsTransformer()
                                           )

DELETE_INITIAL_WORD_TRANSFORMER = NameAndValue('DELETE_INITIAL_WORD_TRANSFORMER',
                                               string_transformers.DeleteInitialWordTransformer()
                                               )

TO_UPPER_CASE_TRANSFORMER = NameAndValue('TO_UPPER_CASE_TRANSFORMER',
                                         string_transformers.MyToUppercaseTransformer()
                                         )


def symbol_container_of(transformer: StringTransformer) -> SymbolContainer:
    return symbol_utils.container(
        string_transformer.StringTransformerSdvConstantTestImpl(transformer)
    )


SYMBOL_TABLE = SymbolTable({

    DELETE_EVERYTHING_TRANSFORMER.name:
        symbol_container_of(DELETE_EVERYTHING_TRANSFORMER.value),

    DUPLICATE_WORDS_TRANSFORMER.name:
        symbol_container_of(DUPLICATE_WORDS_TRANSFORMER.value),

    DELETE_INITIAL_WORD_TRANSFORMER.name:
        symbol_container_of(DELETE_INITIAL_WORD_TRANSFORMER.value),

    TO_UPPER_CASE_TRANSFORMER.name:
        symbol_container_of(TO_UPPER_CASE_TRANSFORMER.value),
})
