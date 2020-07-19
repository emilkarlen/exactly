from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser, ParserFromTokenParserBase
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand


def program_parser(consume_last_line_if_is_at_eol_after_parse: bool) -> Parser[ProgramSdv]:
    return _ParseAsProgram(consume_last_line_if_is_at_eol_after_parse)


def parse_as_program(token_parser: TokenParser) -> ProgramSdv:
    parser = _ParseAsProgram(consume_last_line_if_is_at_eol_after_parse=True)
    return parser.parse_from_token_parser(token_parser)


def parse_as_command(token_parser: TokenParser) -> CommandSdv:
    parser = _ParseAsCommand(consume_last_line_if_is_at_eol_after_parse=True)
    return parser.parse_from_token_parser(token_parser)


class _ParseAsCommand(ParserFromTokenParserBase[CommandSdv]):
    def __init__(self, consume_last_line_if_is_at_eol_after_parse: bool):
        super().__init__(
            consume_last_line_if_is_at_eol_after_parse=consume_last_line_if_is_at_eol_after_parse
        )

    def parse_from_token_parser(self, parser: TokenParser) -> CommandSdv:
        parser.require_is_not_at_eol('Missing {COMMAND}', _PARSE_FORMAT_MAP)
        arguments = self._arguments(parser)
        return command_sdvs.for_shell(arguments)

    def _arguments(self, parser: TokenParser) -> StringSdv:
        return (
            parse_string.parse_rest_of_line_as_single_string_and_consume_line(parser)
            if self._consume_last_line_if_is_at_eol_after_parse
            else
            parse_string.parse_rest_of_line_as_single_string(parser)
        )


class _ParseAsProgram(ParserFromTokenParserBase[ProgramSdv]):
    def __init__(self, consume_last_line_if_is_at_eol_after_parse: bool):
        super().__init__(
            consume_last_line_if_is_at_eol_after_parse=consume_last_line_if_is_at_eol_after_parse
        )
        self._command_parser = _ParseAsCommand(consume_last_line_if_is_at_eol_after_parse)

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command = self._command_parser.parse_from_token_parser(parser)
        return ProgramSdvForCommand(command,
                                    accumulator.empty())


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
