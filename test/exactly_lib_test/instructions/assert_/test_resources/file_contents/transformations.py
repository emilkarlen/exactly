from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax

REPLACE_ENV_VARS_OPTION_ALTERNATIVES = [
    '',
    option_syntax(instruction_options.WITH_REPLACED_ENV_VARS_OPTION_NAME),
]
