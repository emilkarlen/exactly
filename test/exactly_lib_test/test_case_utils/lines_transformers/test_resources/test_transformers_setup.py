from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import lines_transformer
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import test_transformers
from exactly_lib_test.test_resources.name_and_value import NameAndValue

DUPLICATE_WORDS_TRANSFORMER = NameAndValue('DUPLICATE_WORDS_TRANSFORMER',
                                           test_transformers.DuplicateWordsTransformer()
                                           )

DELETE_INITIAL_WORD_TRANSFORMER = NameAndValue('DELETE_INITIAL_WORD_TRANSFORMER',
                                               test_transformers.DeleteInitialWordTransformer()
                                               )

TO_UPPER_CASE_TRANSFORMER = NameAndValue('TO_UPPER_CASE_TRANSFORMER',
                                         test_transformers.MyToUppercaseTransformer()
                                         )

SYMBOL_TABLE = SymbolTable({
    DUPLICATE_WORDS_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.LinesTransformerResolverConstantTestImpl(
            DUPLICATE_WORDS_TRANSFORMER.value)),

    DELETE_INITIAL_WORD_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.LinesTransformerResolverConstantTestImpl(
            DELETE_INITIAL_WORD_TRANSFORMER.value)),

    TO_UPPER_CASE_TRANSFORMER.name:
        symbol_utils.container(lines_transformer.LinesTransformerResolverConstantTestImpl(
            TO_UPPER_CASE_TRANSFORMER.value)),
})
