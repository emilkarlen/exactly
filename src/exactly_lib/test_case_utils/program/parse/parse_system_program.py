from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.program.command.driver_resolvers import CommandDriverResolverForSystemProgram
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.resolvers import accumulator
from exactly_lib.test_case_utils.program.resolvers.command_program_resolver import ProgramResolverForCommand
from exactly_lib.type_system.value_type import DataValueType


def parse_as_command(parser: TokenParser) -> CommandResolver:
    program_name = parse_string.parse_string_from_token_parser(parser, _PARSE_NAME_CONF)
    additional_arguments = parse_arguments.parse_from_token_parser(parser)
    
    return CommandResolver(CommandDriverResolverForSystemProgram(program_name),
                           additional_arguments)


def parse_as_program(parser: TokenParser) -> ProgramResolver:
    command_resolver = parse_as_command(parser)
    return ProgramResolverForCommand(command_resolver, accumulator.empty())


def command_parser() -> Parser[CommandResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_command)


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)


_PROGRAM_NAME_STRING_REFERENCES_RESTRICTION = string_made_up_by_just_strings(
    'A program name must be defined in terms of {string_type}.'.format(
        string_type=define_symbol.DATA_TYPE_INFO_DICT[DataValueType.STRING].identifier,
    ))

_PARSE_NAME_CONF = parse_string.Configuration('NAME',
                                              _PROGRAM_NAME_STRING_REFERENCES_RESTRICTION)
