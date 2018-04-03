from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.test_case_utils.program.parse import executable_file_executable, executable_file


def parse_executable_file_with_args_from_parse_source(source: ParseSource) -> ExecutableFileWithArgsResolver:
    return executable_file_executable.parse_from_parse_source(source)


def parse_executable_file(parser: TokenParser) -> CommandResolver:
    return executable_file.parse_as_command(parser)
