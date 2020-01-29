from exactly_lib.util.cli_syntax.elements.argument import OptionName

OPTION_PREFIX_CHARACTER = '-'


def is_option_string(string: str) -> bool:
    return string and string[0] == OPTION_PREFIX_CHARACTER


def long_option_syntax(name: str) -> str:
    """
    Syntax for a long option.
    :param name: The option name without any "option" syntax prefix ("--).
    """
    return OPTION_PREFIX_CHARACTER + name


def option_syntax(option_name: OptionName) -> str:
    """
    Renders an :class:`OptionName`

    The long name is used if it exists.
    """
    if option_name.long:
        return long_option_syntax(option_name.long)
    else:
        raise ValueError('missing long option')
