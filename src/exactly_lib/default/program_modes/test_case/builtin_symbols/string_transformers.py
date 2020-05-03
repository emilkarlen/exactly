from exactly_lib.cli.main_program import builtin_symbol_of_custom_symbol
from exactly_lib.symbol.logic.string_transformer import StringTransformerStv
from exactly_lib.test_case_utils.string_transformer import custom_transformers

TO_LOWER_CASE = 'TO_LOWER_CASE'

TO_UPPER_CASE = 'TO_UPPER_CASE'

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'REPLACE_TEST_CASE_DIRS'

_TO_UPPER_SINGLE_LINE_DESCRIPTION = ''

ALL = (
    builtin_symbol_of_custom_symbol(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                                    StringTransformerStv(
                                        custom_transformers.replace_env_vars(EXACTLY_TEST_CASE_DIRS_REPLACEMENT)),
                                    custom_transformers.replace_tcds_paths_doc(),
                                    ),
    builtin_symbol_of_custom_symbol(TO_UPPER_CASE,
                                    StringTransformerStv(custom_transformers.to_upper_case(TO_UPPER_CASE)),
                                    custom_transformers.to_upper_case_doc(),
                                    ),
    builtin_symbol_of_custom_symbol(TO_LOWER_CASE,
                                    StringTransformerStv(custom_transformers.to_lower_case(TO_LOWER_CASE)),
                                    custom_transformers.to_lower_case_doc(),
                                    ),
)
