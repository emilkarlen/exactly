from exactly_lib.default.default_main_program import BuiltinSymbol
from exactly_lib.help.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.test_case_utils.lines_transformers.env_vars_replacement import EnvVarReplacementLinesTransformer
from exactly_lib.test_case_utils.lines_transformers.resolvers import LinesTransformerConstant

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'EXACTLY_TEST_CASE_DIRS_REPLACEMENT'

ALL = (
    BuiltinSymbol(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                  LinesTransformerConstant(EnvVarReplacementLinesTransformer(
                      EXACTLY_TEST_CASE_DIRS_REPLACEMENT
                  )),
                  BuiltinSymbolDocumentation(EXACTLY_TEST_CASE_DIRS_REPLACEMENT),
                  ),
)
