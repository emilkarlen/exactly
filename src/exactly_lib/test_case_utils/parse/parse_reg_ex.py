import re

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a

IGNORE_CASE_OPTION_NAME = a.OptionName(long_name='ignore-case')

IGNORE_CASE_OPTION = option_syntax.option_syntax(IGNORE_CASE_OPTION_NAME)


def parse_regex(parser: TokenParser):
    """Returns a reg-ex object"""
    parser.require_is_not_at_eol(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    is_ignore_case = parser.consume_and_handle_optional_option(False,
                                                               lambda x: True,
                                                               IGNORE_CASE_OPTION_NAME)
    parser.require_is_not_at_eol(_MISSING_STRING_ARGUMENT_FOR_REGEX_ERR_MSG)
    regex_pattern = parser.consume_mandatory_token(_MISSING_STRING_ARGUMENT_FOR_REGEX_ERR_MSG)
    return compile_regex(regex_pattern.string, is_ignore_case)


_MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name

_MISSING_STRING_ARGUMENT_FOR_REGEX_ERR_MSG = 'Missing {} argument for {}'.format(
    syntax_elements.STRING_SYNTAX_ELEMENT.argument.name,
    syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name,
)


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
