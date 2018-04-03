from exactly_lib.help_texts import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.program import component_resolvers
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.external_program.command import command_resolvers
from exactly_lib.test_case_utils.external_program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.parse.parse_string import string_resolver_from_string


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)


def parse_as_program(parser: TokenParser) -> ProgramResolver:
    command_resolver = parse_as_command(parser)
    return ProgramResolver(command_resolver,
                           component_resolvers.no_stdin())


def parse_as_command(parser: TokenParser) -> CommandResolver:
    parser.require_is_not_at_eol('Missing {COMMAND}',
                                 _PARSE_FORMAT_MAP)
    argument_string = parser.consume_current_line_as_plain_string()
    argument = string_resolver_from_string(argument_string)

    if not argument_string:
        msg = instruction_arguments.COMMAND_ARGUMENT.name + ' must be given as argument'
        raise SingleInstructionInvalidArgumentException(msg)

    return command_resolvers.for_shell() \
        .new_with_additional_arguments(list_resolvers.from_string(argument))


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
