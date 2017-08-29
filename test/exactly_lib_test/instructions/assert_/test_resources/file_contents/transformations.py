from exactly_lib.test_case_utils.lines_transformers import parse_lines_transformer
from exactly_lib.util.cli_syntax.option_syntax import option_syntax

REPLACE_ENV_VARS_OPTION_ALTERNATIVES = [
    '',
    option_syntax(
        parse_lines_transformer.WITH_REPLACED_ENV_VARS_OPTION_NAME),
]
