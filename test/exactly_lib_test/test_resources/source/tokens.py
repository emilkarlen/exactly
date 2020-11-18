from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib_test.test_resources.source import layout

OPTIONAL_NEW_LINE = layout.OPTIONAL_NEW_LINE


def option(option_name: str) -> str:
    return option_syntax.long_option_syntax(option_name)
