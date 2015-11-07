import shlex

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException


def spit_arguments_list_string(arguments: str) -> list:
    """
    :raises SingleInstructionInvalidArgumentException: The arguments string cannot be parsed.
    """
    try:
        return shlex.split(arguments)
    except ValueError:
        raise SingleInstructionInvalidArgumentException('Invalid quoting of arguments')


def ensure_is_not_option_argument(argument: str):
    """
    :raises SingleInstructionInvalidArgumentException: The arguments is an option argument.
    """
    if argument[0] == '-':
        raise SingleInstructionInvalidArgumentException('An option argument was not expected here: {}'.format(argument))
