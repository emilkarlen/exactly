import sys

from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import PARSE_RESULT
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import list_sdvs, path_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsSdv
from exactly_lib.type_system.data import paths
from exactly_lib.util.cli_syntax import option_parsing


class _Parser(parsers.ParserFromTokenParserBase[ExecutableFileWithArgsSdv]):
    def __init__(self, relativity: RelOptionArgumentConfiguration):
        super().__init__(False, False)
        self._relativity = relativity

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return parse_from_token_parser(parser, self._relativity)


def parser(relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
           ) -> Parser[ExecutableFileWithArgsSdv]:
    return _Parser(relativity)


def parse_from_parse_source(source: ParseSource,
                            relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
                            ) -> ExecutableFileWithArgsSdv:
    with token_stream_parser.from_parse_source(source) as token_parser:
        return parse_from_token_parser(token_parser, relativity)


def parse_from_token_parser(token_parser: TokenParser,
                            relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
                            ) -> ExecutableFileWithArgsSdv:
    return _parse(token_parser.token_stream, relativity)


def _parse(tokens: TokenStream,
           relativity: RelOptionArgumentConfiguration) -> ExecutableFileWithArgsSdv:
    """
    :param tokens: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    if tokens.is_null:
        parse_path.parse_path(tokens, conf=relativity)  # will raise exception
    the_path = _parse_exe_path(tokens, relativity)
    return ExecutableFileWithArgsSdv(the_path,
                                     list_sdvs.empty())


def _parse_exe_path(tokens: TokenStream,
                    relativity: RelOptionArgumentConfiguration) -> PathSdv:
    token = tokens.head
    if token.is_plain and option_parsing.matches(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME, token.string):
        tokens.consume()
        return path_sdvs.constant(paths.absolute_file_name(sys.executable))
    else:
        return parse_path.parse_path(tokens, conf=relativity)
