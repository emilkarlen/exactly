import sys

from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import list_sdvs, path_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.test_case_utils.parse.token_parser_extra import from_parse_source
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.type_system.data import paths
from exactly_lib.util.cli_syntax import option_parsing


def parse_from_parse_source(source: ParseSource) -> ExecutableFileWithArgsResolver:
    with from_parse_source(source) as token_parser:
        return parse_from_token_parser(token_parser)


def parse_from_token_parser(token_parser: TokenParser) -> ExecutableFileWithArgsResolver:
    return _parse(token_parser.token_stream)


def _parse(tokens: TokenStream) -> ExecutableFileWithArgsResolver:
    """
    :param tokens: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    if tokens.is_null:
        parse_path.parse_path(tokens, conf=syntax_elements.REL_OPTION_ARG_CONF)  # will raise exception
    the_path = _parse_exe_path(tokens)
    return ExecutableFileWithArgsResolver(the_path,
                                          list_sdvs.empty())


def _parse_exe_path(tokens: TokenStream) -> PathSdv:
    token = tokens.head
    if token.is_plain and option_parsing.matches(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME, token.string):
        tokens.consume()
        return path_sdvs.constant(paths.absolute_file_name(sys.executable))
    else:
        return parse_path.parse_path(tokens, conf=syntax_elements.REL_OPTION_ARG_CONF)
