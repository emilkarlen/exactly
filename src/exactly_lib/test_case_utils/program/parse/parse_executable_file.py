from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable
from exactly_lib.test_case_utils.program.resolvers import accumulator
from exactly_lib.test_case_utils.program.resolvers.command_program_resolver import ProgramResolverForCommand


def parse_as_command(parser: TokenParser) -> CommandResolver:
    command_resolver = parse_executable_file_executable.parse_from_token_parser(parser).as_command
    additional_arguments = parse_arguments.parse_from_token_parser(parser)
    return command_resolver.new_with_additional_arguments(additional_arguments)


def parse_as_program(parser: TokenParser) -> ProgramResolver:
    command_resolver = parse_as_command(parser)
    return ProgramResolverForCommand(command_resolver, accumulator.empty())


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)
