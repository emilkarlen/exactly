from exactly_lib.section_document.element_parsers import token_stream_parsing as parsing
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.program import arguments_resolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_list, parse_string, parse_file_ref
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.command import argument_resolvers
from exactly_lib.util.parse import token_matchers

REL_OPTIONS_CONF = rel_opts_configuration.RelOptionsConfiguration(
    rel_opts_configuration.RELATIVITY_VARIANTS_FOR_ALL_EXCEPT_RESULT,
    RelOptionType.REL_HOME_CASE)

REL_OPT_ARG_CONF = RelOptionArgumentConfiguration(REL_OPTIONS_CONF,
                                                  syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME.name,
                                                  True)


def parser(consume_last_line_if_is_at_eol_after_parse: bool = False) -> Parser[ArgumentsResolver]:
    return _Parser(consume_last_line_if_is_at_eol_after_parse)


def parse(source: ParseSource) -> ArgumentsResolver:
    return parser().parse(source)


def parse_from_token_parser(token_parser: TokenParser) -> ArgumentsResolver:
    return parser().parse_from_token_parser(token_parser)


class _Parser(Parser[ArgumentsResolver]):
    def __init__(self, consume_last_line_if_is_at_eol_after_parse: bool = True):
        self._consume_last_line_if_is_at_eol_after_parse = consume_last_line_if_is_at_eol_after_parse
        self._element_choices = [
            parsing.TokenSyntaxSetup(
                token_matchers.is_unquoted_and_equals(syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
                _parse_rest_of_line_as_single_element,
            ),
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(syntax_elements.EXISTING_FILE_OPTION_NAME),
                _parse_existing_file,
            ),
        ]

    def parse_from_token_parser(self, token_parser: TokenParser) -> ArgumentsResolver:
        arguments = argument_resolvers.empty()

        while not token_parser.is_at_eol:
            following_arguments = self._parse_element(token_parser)
            arguments = arguments.new_accumulated(following_arguments)

        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

        return arguments

    def _parse_element(self, token_parser: TokenParser) -> ArgumentsResolver:
        return parsing.parse_mandatory_choice_with_default(token_parser,
                                                           syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME.name,
                                                           self._element_choices,
                                                           _parse_plain_list_element)


def _parse_rest_of_line_as_single_element(token_parser: TokenParser) -> ArgumentsResolver:
    string = parse_string.parse_rest_of_line_as_single_string(token_parser, strip_space=True)
    if not string.has_fragments:
        raise SingleInstructionInvalidArgumentException('Empty contents after ' +
                                                        syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)
    return arguments_resolver.new_without_validation(list_resolvers.from_string(string))


def _parse_existing_file(token_parser: TokenParser) -> ArgumentsResolver:
    file_ref = parse_file_ref.parse_file_ref_from_token_parser(REL_OPT_ARG_CONF, token_parser)
    return argument_resolvers.ref_to_file_that_must_exist(file_ref)


def _parse_plain_list_element(parser: TokenParser) -> ArgumentsResolver:
    token = parser.consume_mandatory_token('Invalid list element')
    element = parse_list.element_of(token)
    return arguments_resolver.new_without_validation(list_resolvers.from_elements([element]))
