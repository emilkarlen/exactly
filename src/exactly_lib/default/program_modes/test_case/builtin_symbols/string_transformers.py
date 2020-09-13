from exactly_lib.cli.main_program import builtin_symbol_of_custom_symbol
from exactly_lib.test_case_utils.string_transformer import custom_transformers
from exactly_lib.type_system.value_type import ValueType

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'REPLACE_TEST_CASE_DIRS'

ALL = (
    builtin_symbol_of_custom_symbol(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                                    ValueType.STRING_TRANSFORMER,
                                    custom_transformers.replace_env_vars(EXACTLY_TEST_CASE_DIRS_REPLACEMENT),
                                    custom_transformers.replace_tcds_paths_doc(),
                                    ),
)
