from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, short_option_syntax


def matches(option_name: OptionName, actual_argument_element: str) -> bool:
    if option_name.long:
        option_syntax = long_option_syntax(option_name.long)
        if actual_argument_element == option_syntax:
            return True
    elif option_name.short:
        option_syntax = short_option_syntax(option_name.short)
        if actual_argument_element == option_syntax:
            return True
    else:
        raise ValueError('Invalid option %s: it has neither a long nor a short name.' %
                         str(option_name))
    return False
