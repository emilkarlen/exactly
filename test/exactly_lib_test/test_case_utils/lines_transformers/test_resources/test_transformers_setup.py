from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import lines_transformer
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.type_system.logic.test_resources import line_transformers

DELETE_EVERYTHING_TRANSFORMER = NameAndValue('DELETE_EVERYTHING_TRANSFORMER',
                                             line_transformers.DeleteEverythingTransformer()
                                             )

DUPLICATE_WORDS_TRANSFORMER = NameAndValue('DUPLICATE_WORDS_TRANSFORMER',
                                           line_transformers.DuplicateWordsTransformer()
                                           )

DELETE_INITIAL_WORD_TRANSFORMER = NameAndValue('DELETE_INITIAL_WORD_TRANSFORMER',
                                               line_transformers.DeleteInitialWordTransformer()
                                               )

TO_UPPER_CASE_TRANSFORMER = NameAndValue('TO_UPPER_CASE_TRANSFORMER',
                                         line_transformers.MyToUppercaseTransformer()
                                         )

SYMBOL_TABLE = SymbolTable({

    DELETE_EVERYTHING_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.StringTransformerResolverConstantTestImpl(
            DELETE_EVERYTHING_TRANSFORMER.value)),

    DUPLICATE_WORDS_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.StringTransformerResolverConstantTestImpl(
            DUPLICATE_WORDS_TRANSFORMER.value)),

    DELETE_INITIAL_WORD_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.StringTransformerResolverConstantTestImpl(
            DELETE_INITIAL_WORD_TRANSFORMER.value)),

    TO_UPPER_CASE_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.StringTransformerResolverConstantTestImpl(
            TO_UPPER_CASE_TRANSFORMER.value)),
})
