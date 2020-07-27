from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand


def parser_of_program(
        exe_file_relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
) -> Parser[ProgramSdv]:
    return _ParserOfProgram(exe_file_relativity)


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
        self._relativity_of_exe_file = relativity_of_exe_file
        self._additional_commands_parser = parse_arguments.parser()

    def parse_from_token_parser(self, parser: TokenParser) -> CommandSdv:
        program = parse_executable_file_executable.parse_from_token_parser(parser,
                                                                           self._relativity_of_exe_file)
        command_sdv = program.as_command
        additional_arguments = self._additional_commands_parser.parse_from_token_parser(parser)
        return command_sdv.new_with_additional_arguments(additional_arguments)


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
        return ProgramSdvForCommand(command_sdv, accumulator.empty())
