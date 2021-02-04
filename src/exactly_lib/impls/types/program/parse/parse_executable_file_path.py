import sys

from exactly_lib.impls.types.path import parse_path
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.parse import token_matchers


def parser(relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
           ) -> Parser[PathSdv]:
    return _Parser(relativity)


class _Parser(parsers.ParserFromTokenParserBase[PathSdv]):
    def __init__(self, relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF):
        super().__init__(False, False)
        self._path_parser = parse_path.PathParser(relativity)
        self._is_python_exe_option = token_matchers.is_option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME)

    def parse_from_token_parser(self, parser: TokenParser) -> PathSdv:
        if parser.has_valid_head_token() and self._is_python_exe_option.matches(parser.head):
            parser.consume_head()
            return path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable))
        else:
            return self._path_parser.parse_from_token_parser(parser)
