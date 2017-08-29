import re

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException


def compile_regex(regex_pattern: str):
    """
    :param regex_pattern: The parsed regex pattern

    :return: The compiled regex
    :raises SingleInstructionInvalidArgumentException: The regex has invalid syntax.
    """
    try:
        return re.compile(regex_pattern)
    except Exception as ex:
        err_msg = "Invalid {}: '{}'".format(instruction_arguments.REG_EX.name, str(ex))
        raise SingleInstructionInvalidArgumentException(err_msg)
