from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.impls.types.program.command import command_sdvs
from exactly_lib.impls.types.program.parse import parse_arguments
from exactly_lib.impls.types.program.parse import parse_executable_file_path
from exactly_lib.impls.types.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv


def parser_of_program(
        exe_file_relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
) -> Parser[ProgramSdv]:
    return _ParserOfProgram(exe_file_relativity)


def parser_of_command(
        exe_file_relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
) -> Parser[CommandSdv]:
    return _ParserOfCommand(exe_file_relativity)


def parse_as_command(token_parser: TokenParser,
                     exe_file_relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
                     ) -> CommandSdv:
    parser = _ParserOfCommand(exe_file_relativity)
    return parser.parse_from_token_parser(token_parser)


def parse_as_program(token_parser: TokenParser) -> ProgramSdv:
    parser = parser_of_program()
    return parser.parse_from_token_parser(token_parser)


class _ParserOfCommand(ParserFromTokenParserBase[CommandSdv]):
    def __init__(self, relativity_of_exe_file: RelOptionArgumentConfiguration):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False,
                         consume_last_line_if_is_at_eof_after_parse=False)
        self._arguments_parser = parse_arguments.parser()
        self._exe_file_parser = parse_executable_file_path.parser(relativity_of_exe_file)

    def parse_from_token_parser(self, parser: TokenParser) -> CommandSdv:
        exe_file = self._exe_file_parser.parse_from_token_parser(parser)
        arguments = self._arguments_parser.parse_from_token_parser(parser)
        return command_sdvs.for_executable_file(exe_file, arguments)


class _ParserOfProgram(ParserFromTokenParserBase[ProgramSdv]):
    def __init__(self,
                 relativity_of_exe_file: RelOptionArgumentConfiguration,
                 consume_last_line_if_is_at_eol_after_parse: bool = True,
                 ):
        super().__init__(consume_last_line_if_is_at_eol_after_parse,
                         False)
        self._command_parser = _ParserOfCommand(relativity_of_exe_file)

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command_sdv = self._command_parser.parse_from_token_parser(parser)
        return ProgramSdvForCommand(command_sdv, AccumulatedComponents.empty())
