from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand


def parser_of_program(consume_last_line_if_is_at_eol_after_parse: bool = True) -> Parser[ProgramSdv]:
    return _ParserOfProgram(consume_last_line_if_is_at_eol_after_parse)


def parse_as_command(token_parser: TokenParser) -> CommandSdv:
    parser = _ParserOfCommand(consume_last_line_if_is_at_eol_after_parse=True)
    return parser.parse_from_token_parser(token_parser)


def parse_as_program(token_parser: TokenParser) -> ProgramSdv:
    parser = parser_of_program(consume_last_line_if_is_at_eol_after_parse=True)
    return parser.parse_from_token_parser(token_parser)


class _ParserOfCommand(Parser[CommandSdv]):
    def __init__(self,
                 consume_last_line_if_is_at_eol_after_parse: bool = True,
                 ):
        super().__init__(consume_last_line_if_is_at_eol_after_parse,
                         consume_last_line_if_is_at_eof_after_parse=True)
        self._additional_commands_parser = parse_arguments.parser(consume_last_line_if_is_at_eol_after_parse)

    def parse_from_token_parser(self, parser: TokenParser) -> CommandSdv:
        command_sdv = parse_executable_file_executable.parse_from_token_parser(parser).as_command
        additional_arguments = self._additional_commands_parser.parse_from_token_parser(parser)
        return command_sdv.new_with_additional_arguments(additional_arguments)


class _ParserOfProgram(Parser[ProgramSdv]):
    def __init__(self,
                 consume_last_line_if_is_at_eol_after_parse: bool = True,
                 ):
        super().__init__(consume_last_line_if_is_at_eol_after_parse,
                         False)
        self._command_parser = _ParserOfCommand(
            consume_last_line_if_is_at_eol_after_parse=consume_last_line_if_is_at_eol_after_parse,
        )

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command_sdv = self._command_parser.parse_from_token_parser(parser)
        return ProgramSdvForCommand(command_sdv, accumulator.empty())
