from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.external_program.command_and_stdin import CommandAndStdinResolver


class CommandAndStdinResolverParser:
    def parse(self, source: ParseSource) -> CommandAndStdinResolver:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> CommandAndStdinResolver:
        raise NotImplementedError('abstract method')
