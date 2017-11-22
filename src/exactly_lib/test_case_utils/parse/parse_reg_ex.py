import re

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a

IGNORE_CASE_OPTION_NAME = a.OptionName(long_name='ignore-case')

IGNORE_CASE_OPTION = option_syntax.option_syntax(IGNORE_CASE_OPTION_NAME)


def parse_regex(parser: TokenParserPrime):
    """Returns a reg-ex object"""
    parser.require_is_not_at_eol(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    is_ignore_case = parser.consume_and_return_true_if_first_argument_is_unquoted_and_equals(IGNORE_CASE_OPTION)
    parser.require_is_not_at_eol(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    regex_pattern = parser.consume_mandatory_token(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    return compile_regex(regex_pattern.string, is_ignore_case)


_MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name


def compile_regex(regex_pattern: str, is_ignore_case: bool):
    """
    :param regex_pattern: The parsed regex pattern

    :return: The compiled regex
    :raises SingleInstructionInvalidArgumentException: The regex has invalid syntax.
    """
    try:
        flags = 0
        if is_ignore_case:
            flags = re.IGNORECASE
        return re.compile(regex_pattern, flags)
    except Exception as ex:
        err_msg = "Invalid {}: '{}'".format(instruction_arguments.REG_EX.name, str(ex))
        raise SingleInstructionInvalidArgumentException(err_msg)
