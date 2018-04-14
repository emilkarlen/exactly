from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.program.command import command_resolvers
from exactly_lib.test_case_utils.program.resolvers import accumulator
from exactly_lib.test_case_utils.program.resolvers.command_program_resolver import ProgramResolverForCommand


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)


def parse_as_program(parser: TokenParser) -> ProgramResolver:
    command_resolver = parse_as_command(parser)
    return ProgramResolverForCommand(command_resolver,
                                     accumulator.empty())


def parse_as_command(parser: TokenParser) -> CommandResolver:
    parser.require_is_not_at_eol('Missing {COMMAND}', _PARSE_FORMAT_MAP)
    argument = parse_string.parse_rest_of_line_as_single_string_and_consume_line(parser)

    return command_resolvers.for_shell(argument)


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
