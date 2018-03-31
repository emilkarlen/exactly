from typing import TypeVar, Generic, Callable

from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, TokenParser
from exactly_lib.section_document.parse_source import ParseSource

PARSE_RESULT = TypeVar('PARSE_RESULT')
T = TypeVar('T')


class Parser(Generic[PARSE_RESULT]):
    def parse(self, source: ParseSource) -> PARSE_RESULT:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        raise NotImplementedError('abstract method')


class ParserFromSimpleParser(Parser[PARSE_RESULT]):
    def __init__(self,
                 simple: Parser[T],
                 transformer: Callable[[T], PARSE_RESULT]):
        self._simple = simple
        self._transformer = transformer

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._transformer(self._simple.parse_from_token_parser(parser))


class ParserFromTokenParserFunction(Parser[PARSE_RESULT]):
    def __init__(self, parser_function: Callable[[TokenParser], PARSE_RESULT]):
        self._parser_function = parser_function

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._parser_function(parser)
