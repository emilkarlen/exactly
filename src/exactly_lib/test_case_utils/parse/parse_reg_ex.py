import re

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime


def parse_regex(parser: TokenParserPrime):
    """Returns a reg-ex object"""
    parser.require_is_not_at_eol(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    regex_pattern = parser.consume_mandatory_token(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    return compile_regex(regex_pattern.string)


_MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name


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
