from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.program.command import command_sdvs
from exactly_lib.impls.types.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv


def program_parser() -> Parser[ProgramSdv]:
    return _ParseAsProgram()


def parse_as_program(token_parser: TokenParser) -> ProgramSdv:
    parser = _ParseAsProgram()
    return parser.parse_from_token_parser(token_parser)


def parse_as_command(token_parser: TokenParser) -> CommandSdv:
    parser = _ParseAsCommand()
    return parser.parse_from_token_parser(token_parser)


class _ParseAsCommand(ParserFromTokenParserBase[CommandSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)

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
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)
        self._command_parser = _ParseAsCommand()

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command = self._command_parser.parse_from_token_parser(parser)
        return ProgramSdvForCommand(command,
                                    AccumulatedComponents.empty())


_PARSE_FORMAT_MAP = {
    'COMMAND': syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.singular_name
}
