import shlex

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.parse.token import Token


def split_arguments_list_string(arguments: str) -> list:
    """
    :raises SingleInstructionInvalidArgumentException: The arguments string cannot be parsed.
    """
    try:
        return shlex.split(arguments)
    except ValueError:
        raise SingleInstructionInvalidArgumentException('Invalid quoting of arguments')


def is_option_argument(argument: str) -> bool:
    return argument[0] == '-'


def is_option_token(token: Token) -> bool:
    return token.source_string[0] == '-'


def ensure_is_not_option_argument(argument: str):
    """
    :raises SingleInstructionInvalidArgumentException: The arguments is an option argument.
    """
    if is_option_argument(argument):
        raise SingleInstructionInvalidArgumentException('An option argument was not expected here: {}'.format(argument))
