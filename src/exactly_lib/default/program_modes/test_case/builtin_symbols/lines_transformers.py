from exactly_lib.cli.main_program import BuiltinSymbol
from exactly_lib.test_case_utils.lines_transformer import env_vars_replacement
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'REPLACE_TEST_CASE_DIRS'

_RESOLVER = LinesTransformerConstant(
    env_vars_replacement.EnvVarReplacementLinesTransformer())

_SINGLE_LINE_DESCRIPTION = ''

ALL = (
    BuiltinSymbol(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                  _RESOLVER,
                  env_vars_replacement.SINGLE_LINE_DESCRIPTION,
                  env_vars_replacement.with_replaced_env_vars_help(),
                  ),
)
