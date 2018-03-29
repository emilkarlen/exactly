from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.test_case_utils.external_program.command import command_resolvers
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.external_program.command_and_stdin import CommandAndStdinResolver
from exactly_lib.test_case_utils.external_program.program import ProgramResolver
from exactly_lib.test_case_utils.parse.parse_executable_file import parse
from exactly_lib.test_case_utils.parse.token_parser_extra import from_parse_source


class CommandAndStdinParser(Parser[CommandAndStdinResolver]):
    def parse_from_token_parser(self, parser: TokenParser) -> CommandAndStdinResolver:
        raise NotImplementedError('abstract method')


class ProgramParser(Parser[ProgramResolver]):
    def parse_from_token_parser(self, parser: TokenParser) -> ProgramResolver:
        raise NotImplementedError('abstract method')


def parse_from_parse_source_new(source: ParseSource) -> CommandResolver:
    with from_parse_source(source) as token_parser:
        return command_from_token_parser(token_parser)


def command_from_token_parser(token_parser: TokenParser) -> CommandResolver:
    exe_file = parse(token_parser.token_stream)
    command_resolver = command_resolvers.for_executable_file(exe_file.executable_file)
    return command_resolver.new_with_additional_arguments(exe_file.arguments)


def command_and_stdin_from_token_parser(token_parser: TokenParser) -> CommandAndStdinResolver:
    command = command_from_token_parser(token_parser)
    return CommandAndStdinResolver(command)
