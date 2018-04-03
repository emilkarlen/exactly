from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.program import arguments_resolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.test_case_utils.parse import parse_list
from exactly_lib.test_case_utils.parse import parse_string, parse_file_ref
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable
from exactly_lib.test_case_utils.program.resolvers import accumulator
from exactly_lib.test_case_utils.program.resolvers.command_program_resolver import ProgramResolverForCommand


def parse_as_command(parser: TokenParser) -> CommandResolver:
    command_resolver = parse_executable_file_executable.parse_from_token_parser(parser).as_command
    additional_arguments = _parse_additional_arguments(parser)
    return command_resolver.new_with_additional_arguments(additional_arguments)


def parse_as_program(parser: TokenParser) -> ProgramResolver:
    command_resolver = parse_as_command(parser)
    return ProgramResolverForCommand(command_resolver, accumulator.empty())


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)


def _parse_additional_arguments(token_parser: TokenParser) -> ArgumentsResolver:
    if token_parser.is_at_eol:
        return _execute(token_parser)

    setup = {
        syntax_elements.INTERPRET_OPTION: _interpret,
        syntax_elements.SOURCE_OPTION: _source,
        syntax_elements.OPTIONS_SEPARATOR_ARGUMENT: _execute,
    }

    option = token_parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(setup.keys())
    if option is not None:
        return setup[option](token_parser)
    else:
        return _execute(token_parser)


def _execute(token_parser: TokenParser) -> ArgumentsResolver:
    arguments = parse_list.parse_list_from_token_parser(token_parser)
    return ArgumentsResolver(arguments=arguments)


def _interpret(token_parser: TokenParser) -> ArgumentsResolver:
    file_to_interpret = parse_file_ref.parse_file_ref_from_token_parser(parse_file_ref.ALL_REL_OPTIONS_CONFIG,
                                                                        token_parser)
    file_to_interpret_check = FileRefCheck(file_to_interpret,
                                           file_properties.must_exist_as(file_properties.FileType.REGULAR))
    file_to_interpret_validator = FileRefCheckValidator(file_to_interpret_check)
    remaining_arguments = parse_list.parse_list_from_token_parser(token_parser)
    all_additional_arguments = list_resolvers.concat([
        list_resolvers.from_string(string_resolvers.from_file_ref_resolver(file_to_interpret)),
        remaining_arguments,
    ])
    return ArgumentsResolver(all_additional_arguments,
                             [file_to_interpret_validator])


def _source(token_parser: TokenParser) -> ArgumentsResolver:
    if token_parser.is_at_eol:
        msg = 'Missing {SOURCE} argument for option {option}'.format(SOURCE=syntax_elements.SOURCE_SYNTAX_ELEMENT_NAME,
                                                                     option=syntax_elements.SOURCE_OPTION)
        raise SingleInstructionInvalidArgumentException(msg)
    remaining_arguments_str = token_parser.consume_current_line_as_plain_string()
    source_resolver = parse_string.string_resolver_from_string(remaining_arguments_str.strip())
    return arguments_resolver.new_without_validation(list_resolvers.from_string(source_resolver))
