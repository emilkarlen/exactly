from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax


def matches(option_name: OptionName, actual_argument_element: str) -> bool:
    option_syntax = long_option_syntax(option_name.long)
    return actual_argument_element == option_syntax
