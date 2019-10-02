import exactly_lib_test.type_system.logic.string_transformer.test_resources
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import string_transformer
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.type_system.logic.test_resources import string_transformers

DELETE_EVERYTHING_TRANSFORMER = NameAndValue('DELETE_EVERYTHING_TRANSFORMER',
                                             exactly_lib_test.type_system.logic.string_transformer.test_resources.DeleteEverythingTransformer()
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

SYMBOL_TABLE = SymbolTable({

    DELETE_EVERYTHING_TRANSFORMER.name:
        symbol_utils.container(string_transformer.StringTransformerResolverConstantTestImpl(
            DELETE_EVERYTHING_TRANSFORMER.value)),

    DUPLICATE_WORDS_TRANSFORMER.name:
        symbol_utils.container(string_transformer.StringTransformerResolverConstantTestImpl(
            DUPLICATE_WORDS_TRANSFORMER.value)),

    DELETE_INITIAL_WORD_TRANSFORMER.name:
        symbol_utils.container(string_transformer.StringTransformerResolverConstantTestImpl(
            DELETE_INITIAL_WORD_TRANSFORMER.value)),

    TO_UPPER_CASE_TRANSFORMER.name:
        symbol_utils.container(string_transformer.StringTransformerResolverConstantTestImpl(
            TO_UPPER_CASE_TRANSFORMER.value)),
})
