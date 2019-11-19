from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand


def program_parser() -> Parser[ProgramSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)


def parse_as_program(parser: TokenParser) -> ProgramSdv:
    command_sdv = parse_as_command(parser)
    return ProgramSdvForCommand(command_sdv,
                                accumulator.empty())


def parse_as_command(parser: TokenParser) -> CommandSdv:
    parser.require_is_not_at_eol('Missing {COMMAND}', _PARSE_FORMAT_MAP)
    argument = parse_string.parse_rest_of_line_as_single_string_and_consume_line(parser)

    return command_sdvs.for_shell(argument)


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
