from exactly_lib.section_document.element_parsers import token_stream_parsing as parsing
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_list, parse_string, parse_path
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.util.parse import token_matchers

REL_OPTIONS_CONF = rel_opts_configuration.RelOptionsConfiguration(
    rel_opts_configuration.RELATIVITY_VARIANTS_FOR_ALL_EXCEPT_RESULT,
    RelOptionType.REL_HDS_CASE)

REL_OPT_ARG_CONF = RelOptionArgumentConfiguration(REL_OPTIONS_CONF,
                                                  syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME.name,
                                                  True)


def parser() -> Parser[ArgumentsSdv]:
    return _PARSE


class _Parser(ParserFromTokenParserBase[ArgumentsSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False,
                         consume_last_line_if_is_at_eof_after_parse=False)
        self._element_choices = [
            parsing.TokenSyntaxSetup(
                token_matchers.is_unquoted_and_equals(syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
                _parse_rest_of_line_as_single_element,
            ),
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(syntax_elements.EXISTING_FILE_OPTION_NAME),
                _parse_existing_file,
            ),
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(syntax_elements.EXISTING_DIR_OPTION_NAME),
                _parse_existing_dir,
            ),
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(syntax_elements.EXISTING_PATH_OPTION_NAME),
                _parse_existing_path,
            ),
        ]

    def parse_from_token_parser(self, token_parser: TokenParser) -> ArgumentsSdv:
        arguments = arguments_sdvs.empty()

        while not token_parser.is_at_eol:
            following_arguments = self._parse_element(token_parser)
            arguments = arguments.new_accumulated(following_arguments)

        if self._consume_last_line_if_is_at_eol_after_parse:
            token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        else:
            token_parser.consume_remaining_part_of_current_line_as_string()

        return arguments

    def _parse_element(self, token_parser: TokenParser) -> ArgumentsSdv:
        return parsing.parse_mandatory_choice_with_default(token_parser,
                                                           syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME.name,
                                                           self._element_choices,
                                                           _parse_plain_list_element)


def _parse_rest_of_line_as_single_element(token_parser: TokenParser) -> ArgumentsSdv:
    string = parse_string.parse_rest_of_line_as_single_string(token_parser, strip_space=True)
    if not string.has_fragments:
        raise SingleInstructionInvalidArgumentException('Empty contents after ' +
                                                        syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)
    return arguments_sdvs.new_without_validation(list_sdvs.from_string(string))


def _parse_existing_file(token_parser: TokenParser) -> ArgumentsSdv:
    path = parse_path.parse_path_from_token_parser(REL_OPT_ARG_CONF, token_parser)
    return arguments_sdvs.ref_to_file_that_must_exist(path, FileType.REGULAR)


def _parse_existing_dir(token_parser: TokenParser) -> ArgumentsSdv:
    path = parse_path.parse_path_from_token_parser(REL_OPT_ARG_CONF, token_parser)
    return arguments_sdvs.ref_to_file_that_must_exist(path, FileType.DIRECTORY)


def _parse_existing_path(token_parser: TokenParser) -> ArgumentsSdv:
    path = parse_path.parse_path_from_token_parser(REL_OPT_ARG_CONF, token_parser)
    return arguments_sdvs.ref_to_path_that_must_exist(path)


def _parse_plain_list_element(parser: TokenParser) -> ArgumentsSdv:
    token = parser.consume_mandatory_token('Invalid list element')
    element = parse_list.element_of(token)
    return arguments_sdvs.new_without_validation(list_sdvs.from_elements([element]))


_PARSE = _Parser()
