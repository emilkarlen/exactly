def short_option_syntax(character: str) -> str:
    """
    Syntax for a short option.
    :param character: The single option character.
    """
    return '-' + character


def long_option_syntax(name: str) -> str:
    """
    Syntax for a long option.
    :param name: The option name without any "option" syntax prefix ("--).
    """
    return '--' + name
