from typing import TypeVar, Generic, Callable

from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, TokenParser
from exactly_lib.section_document.parse_source import ParseSource

PARSE_RESULT = TypeVar('PARSE_RESULT')
T = TypeVar('T')


class Parser(Generic[PARSE_RESULT]):
    def __init__(self,
                 consume_last_line_if_is_at_eol_after_parse: bool = True,
                 consume_last_line_if_is_at_eof_after_parse: bool = False):
        self._consume_last_line_if_is_at_eol_after_parse = consume_last_line_if_is_at_eol_after_parse
        self._consume_last_line_if_is_at_eof_after_parse = consume_last_line_if_is_at_eof_after_parse

    def parse(self, source: ParseSource) -> PARSE_RESULT:
        with from_parse_source(source,
                               self._consume_last_line_if_is_at_eol_after_parse,
                               self._consume_last_line_if_is_at_eof_after_parse) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        raise NotImplementedError('abstract method')


class ParserWithCurrentLineVariants(Generic[PARSE_RESULT], Parser[PARSE_RESULT]):
    """
    Parser that can expect parsed object on either current line or any following line.

    Ugly sub class ing of :class:`Parser`. Want to "add current-line-variants"
    to :class:`Parser`, but cannot do it in one step.  So introduces this class in the
    mean time.
    """

    def parse(self,
              source: ParseSource,
              must_be_on_current_line: bool = False,
              ) -> PARSE_RESULT:
        with from_parse_source(source,
                               self._consume_last_line_if_is_at_eol_after_parse,
                               self._consume_last_line_if_is_at_eof_after_parse) as parser:
            return self.parse_from_token_parser(parser, must_be_on_current_line)

    def parse_from_token_parser(self,
                                tokens: TokenParser,
                                must_be_on_current_line: bool = False,
                                ) -> PARSE_RESULT:
        raise NotImplementedError('abstract method')


class ParserFromSimpleParser(Parser[PARSE_RESULT]):
    def __init__(self,
                 simple: Parser[T],
                 transformer: Callable[[T], PARSE_RESULT],
                 consume_last_line_if_is_at_eol_after_parse: bool = True):
        super().__init__(consume_last_line_if_is_at_eol_after_parse)
        self._simple = simple
        self._transformer = transformer

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._transformer(self._simple.parse_from_token_parser(parser))


class ParserFromTokenParserFunction(Parser[PARSE_RESULT]):
    def __init__(self,
                 parser_function: Callable[[TokenParser], PARSE_RESULT],
                 consume_last_line_if_is_at_eol_after_parse: bool = True):
        super().__init__(consume_last_line_if_is_at_eol_after_parse)
        self._parser_function = parser_function

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._parser_function(parser)
