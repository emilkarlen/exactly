from exactly_lib.cli.main_program import BuiltinSymbol
from exactly_lib.test_case_utils.lines_transformer import env_vars_replacement, case_converters
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.util.textformat.structure.document import empty_section_contents

EXACTLY_TEST_CASE_DIRS_REPLACEMENT = 'REPLACE_TEST_CASE_DIRS'

_TO_UPPER_SINGLE_LINE_DESCRIPTION = ''

ALL = (
    BuiltinSymbol(EXACTLY_TEST_CASE_DIRS_REPLACEMENT,
                  LinesTransformerConstant(env_vars_replacement.EnvVarReplacementLinesTransformer()),
                  env_vars_replacement.SINGLE_LINE_DESCRIPTION,
                  env_vars_replacement.with_replaced_env_vars_help(),
                  ),
    BuiltinSymbol('TO_UPPER_CASE',
                  LinesTransformerConstant(case_converters.ToUpperCaseLinesTransformer()),
                  'Converts all cased characters to uppercase',
                  empty_section_contents(),
                  ),
    BuiltinSymbol('TO_LOWER_CASE',
                  LinesTransformerConstant(case_converters.ToLowerCaseLinesTransformer()),
                  'Converts all cased characters to lowercase',
                  empty_section_contents(),
                  ),
)
