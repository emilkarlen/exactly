from exactly_lib.named_element import resolver_structure
from exactly_lib.test_case_utils.lines_transformers.env_vars_replacement import EnvVarReplacementLinesTransformer
from exactly_lib.test_case_utils.lines_transformers.resolvers import LinesTransformerConstant
from exactly_lib.util import symbol_table

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'EXACTLY_TEST_CASE_DIRS_REPLACEMENT'

ALL = (
    symbol_table.Entry(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                       resolver_structure.container_of_builtin(
                           LinesTransformerConstant(EnvVarReplacementLinesTransformer(
                               EXACTLY_TEST_CASE_DIRS_REPLACEMENT
                           ))
                       )),
)
