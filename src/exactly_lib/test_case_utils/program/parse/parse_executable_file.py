from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand


def parse_as_command(parser: TokenParser) -> CommandSdv:
    command_sdv = parse_executable_file_executable.parse_from_token_parser(parser).as_command
    additional_arguments = parse_arguments.parse_from_token_parser(parser)
    return command_sdv.new_with_additional_arguments(additional_arguments)


def parse_as_program(parser: TokenParser) -> ProgramSdv:
    command_sdv = parse_as_command(parser)
    return ProgramSdvForCommand(command_sdv, accumulator.empty())


def program_parser() -> Parser[ProgramSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)
