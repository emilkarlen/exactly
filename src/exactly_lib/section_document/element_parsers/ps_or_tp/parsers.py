from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

from exactly_lib.section_document.element_parsers.ps_or_tp.parser import PARSE_RESULT, Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, TokenParser
from exactly_lib.section_document.parse_source import ParseSource

T = TypeVar('T')


class ParserFromTokenParserBase(Generic[PARSE_RESULT], Parser[PARSE_RESULT], ABC):
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

    @abstractmethod
    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        pass


class ParserWithCurrentLineVariants(Generic[PARSE_RESULT], ParserFromTokenParserBase[PARSE_RESULT]):
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


class ParserFromTokenParserFunction(ParserFromTokenParserBase[PARSE_RESULT]):
    def __init__(self,
                 parser_function: Callable[[TokenParser], PARSE_RESULT],
                 consume_last_line_if_is_at_eol_after_parse: bool = True):
        super().__init__(consume_last_line_if_is_at_eol_after_parse)
        self._parser_function = parser_function

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._parser_function(parser)
