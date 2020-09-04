import shlex
from typing import List

from exactly_lib.util.argument_parsing_utils import ArgumentParsingError


def shlex_split(component: str, value: str) -> List[str]:
    """
    :param component: Name of object that is splitted.
    :param value: String to split.
    :return: value splitted according to shell syntax.
    :raises ArgumentParsingError: Just white space or invalid shell syntax.
    """
    value = value.strip()
    if value == '':
        raise ArgumentParsingError('{}: Must contain at least one word'.format(component))
    try:
        return shlex.split(value)
    except ValueError as ex:
        raise ArgumentParsingError('{}: {}\n{}'.format(component, value, str(ex)))
