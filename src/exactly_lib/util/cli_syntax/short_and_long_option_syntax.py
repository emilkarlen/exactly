from exactly_lib.util.cli_syntax.elements.argument import ShortAndLongOptionName


def short_syntax(character: str) -> str:
    """
    Syntax for a short option.
    :param character: The single option character.
    """
    return '-' + character


def long_syntax(name: str) -> str:
    """
    Syntax for a long option.
    :param name: The option name without any "option" syntax prefix ("--).
    """
    return '--' + name


def option_syntax(option_name: ShortAndLongOptionName) -> str:
    """
    Renders an :class:`OptionName`

    The long name is used if it exists.
    """
    if option_name.long:
        return long_syntax(option_name.long)
    else:
        return short_syntax(option_name.short)
