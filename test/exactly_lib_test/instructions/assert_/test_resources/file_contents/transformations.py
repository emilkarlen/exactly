import exactly_lib.test_case_utils.parse.parse_file_transformer
from exactly_lib.util.cli_syntax.option_syntax import option_syntax

REPLACE_ENV_VARS_OPTION_ALTERNATIVES = [
    '',
    option_syntax(exactly_lib.test_case_utils.parse.parse_file_transformer.WITH_REPLACED_ENV_VARS_OPTION_NAME),
]
