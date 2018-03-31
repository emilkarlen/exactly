from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.external_program.command import command_resolvers
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.parse.parse_executable_file import parse
from exactly_lib.test_case_utils.parse.token_parser_extra import from_parse_source


def parse_executable_file_from_parse_source_new(source: ParseSource) -> CommandResolver:
    with from_parse_source(source) as token_parser:
        return parse_executable_file(token_parser)


def parse_executable_file(token_parser: TokenParser) -> CommandResolver:
    exe_file = parse(token_parser.token_stream)
    return command_resolvers.for_executable_file(exe_file.executable_file) \
        .new_with_additional_arguments(exe_file.arguments)
