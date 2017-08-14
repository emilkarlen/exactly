"""Functionality for accessing a subset of the files in a directory."""
from exactly_lib.help_texts.name_and_cross_ref import Name
from exactly_lib.instructions.utils.parse import token_stream_parse
from exactly_lib.instructions.utils.parse import token_stream_parse_prime
from exactly_lib.instructions.utils.parse.token_stream_parse_prime import TokenParserPrime
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils import file_properties
from exactly_lib.util import dir_contents_selection
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.dir_contents_selection import Selectors

CONCEPT_NAME = Name('selector', 'selectors')

COMMAND_NAME__NAME_SELECTOR = 'name'

COMMAND_NAME__TYPE_SELECTOR = 'type'


class CommandSetup:
    def __init__(self, argument_syntax_element_name: str):
        self.argument_syntax_element_name = argument_syntax_element_name


COMMANDS = {
    COMMAND_NAME__NAME_SELECTOR: CommandSetup('PATTERN'),
    COMMAND_NAME__TYPE_SELECTOR: CommandSetup('TYPE'),
}

AND_OPERATOR = '&'

SELECTION_OPTION = a.option(long_name='selection',
                            argument='SELECTOR')


def every_file_in_dir() -> Selectors:
    return dir_contents_selection.all_files()


def parse_from_parse_source(source: ParseSource,
                            selector_is_mandatory: bool) -> Selectors:
    with token_stream_parse.from_parse_source(source) as tp:
        return parse(tp, selector_is_mandatory)


def parse(parser: TokenParserPrime,
          selector_is_mandatory: bool) -> Selectors:
    parser = token_stream_parse_prime.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)

    selector = parser.parse_optional_command(_SELECTOR_PARSERS)

    if selector is None:
        if selector_is_mandatory:
            return parser.error('Missing {_SELECTOR_} argument.')
        else:
            return dir_contents_selection.all_files()

    ret_val = selector

    while parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(AND_OPERATOR):
        next_selector = parser.parse_mandatory_command(_SELECTOR_PARSERS,
                                                       'Missing {_SELECTOR_} argument.')
        ret_val = dir_contents_selection.and_also(ret_val, next_selector)

    return ret_val


def _error_message(template: str) -> str:
    return template.format_map(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)


def _parse_name_selector(parser: TokenParserPrime) -> Selectors:
    pattern = parser.consume_mandatory_string_argument(
        _ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME)
    return dir_contents_selection.name_matches_pattern(pattern)


def _parse_type_selector(parser: TokenParserPrime) -> Selectors:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return dir_contents_selection.file_type_is(file_type)


_SELECTOR_PARSERS = {
    COMMAND_NAME__NAME_SELECTOR: _parse_name_selector,
    COMMAND_NAME__TYPE_SELECTOR: _parse_type_selector,
}

ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_SELECTOR_': CONCEPT_NAME.singular,
    '_NAME_SELECTOR_': COMMAND_NAME__NAME_SELECTOR,
    '_TYPE_SELECTOR_': COMMAND_NAME__TYPE_SELECTOR,
    '_PATTERN_': COMMANDS[COMMAND_NAME__NAME_SELECTOR].argument_syntax_element_name,
    '_TYPE_': COMMANDS[COMMAND_NAME__TYPE_SELECTOR].argument_syntax_element_name,
}

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_PATTERN_} argument for {_NAME_SELECTOR_}'
