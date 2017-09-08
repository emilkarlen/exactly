from exactly_lib.default.default_main_program import BuiltinSymbol
from exactly_lib.test_case_utils.lines_transformer.env_vars_replacement import EnvVarReplacementLinesTransformer, \
    with_replaced_env_vars_help
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'EXACTLY_TEST_CASE_DIRS_REPLACEMENT'

_RESOLVER = LinesTransformerConstant(EnvVarReplacementLinesTransformer(EXACTLY_TEST_CASE_DIRS_REPLACEMENT))

ALL = (
    BuiltinSymbol(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                  _RESOLVER,
                  with_replaced_env_vars_help(),
                  ),
)
