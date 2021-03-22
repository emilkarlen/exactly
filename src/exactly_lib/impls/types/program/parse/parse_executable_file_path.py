import sys

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.path import parse_path
from exactly_lib.impls.types.program import syntax_elements as _pgm_syntax_elements
from exactly_lib.section_document.element_parsers import token_stream_parsing as _parsing
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.util.parse import token_matchers


def parser(relativity: RelOptionArgumentConfiguration = _pgm_syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
           ) -> Parser[PathSdv]:
    return _Parser(relativity)


class _Parser(parsers.ParserFromTokenParserBase[PathSdv]):
    def __init__(self, relativity: RelOptionArgumentConfiguration = _pgm_syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF):
        super().__init__(False, False)
        self._path_parser = parse_path.PathParser(relativity)
        self._choices = [
            _parsing.TokenSyntaxSetup(
                token_matchers.is_option(_pgm_syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
                self._parse_python_interpreter,
            ),
        ]

    def parse_from_token_parser(self, token_parser: TokenParser) -> PathSdv:
        return _parsing.parse_mandatory_choice_with_default(
            token_parser,
            syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.singular_name,
            self._choices,
            self._parse_explicit_exe_file,
        )

    @staticmethod
    def _parse_python_interpreter(token_parser: TokenParser) -> PathSdv:
        return path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable))

    def _parse_explicit_exe_file(self, token_parser: TokenParser) -> PathSdv:
        return self._path_parser.parse_from_token_parser(token_parser)
