from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.test_case_utils.external_program import syntax_elements
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.external_program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.test_case_utils.external_program.parse_impls import shell_program, \
    executable_file, executable_file_executable
from exactly_lib.test_case_utils.external_program.program_resolver import ProgramResolver


def parse_executable_file_with_args_from_parse_source(source: ParseSource) -> ExecutableFileWithArgsResolver:
    return executable_file_executable.parse_from_parse_source(source)


def parse_executable_file(parser: TokenParser) -> CommandResolver:
    return executable_file.parse_as_command(parser)


def parse_executable_file_as_program(parser: TokenParser) -> ProgramResolver:
    return executable_file.parse_as_program(parser)


def executable_file_program_parser() -> Parser[ProgramResolver]:
    return executable_file.program_parser()


def parse_shell_command_line(parser: TokenParser) -> CommandResolver:
    return shell_program.parse_as_command(parser)


def parse_shell_command_line_as_program(parser: TokenParser) -> ProgramResolver:
    return shell_program.parse_as_program(parser)


def shell_command_line_program_parser() -> Parser[ProgramResolver]:
    return shell_program.program_parser()


def parse_program(parser: TokenParser) -> ProgramResolver:
    if parser.consume_and_return_true_if_first_argument_is_unquoted_and_equals(syntax_elements.SHELL_COMMAND_TOKEN):
        return parse_shell_command_line_as_program(parser)
    else:
        return parse_executable_file_as_program(parser)


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_program)
