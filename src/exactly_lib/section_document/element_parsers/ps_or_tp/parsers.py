from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

from exactly_lib.impls.types.expression.grammar import Grammar, EXPR
from exactly_lib.section_document.element_parsers import instruction_parser_exceptions
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


class ParserFromTokenParserFunction(Generic[PARSE_RESULT], ParserFromTokenParserBase[PARSE_RESULT]):
    def __init__(self,
                 parser_function: Callable[[TokenParser], PARSE_RESULT],
                 consume_last_line_if_is_at_eol_after_parse: bool = True):
        super().__init__(consume_last_line_if_is_at_eol_after_parse)
        self._parser_function = parser_function

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._parser_function(parser)


class CurrentLineMustNotBeEmptyExceptForSpace(Generic[PARSE_RESULT], Parser[PARSE_RESULT]):
    """
    Raises SingleInstructionInvalidArgumentException if current line is empty.
    """

    def __init__(self,
                 with_non_empty_current_line: Parser[PARSE_RESULT],
                 error_message_if_current_line_empty: str,
                 ):
        self._with_non_empty_current_line = with_non_empty_current_line
        self._error_message_if_current_line_empty = error_message_if_current_line_empty

    @staticmethod
    def of_mandatory_element(element_name: str,
                             with_non_empty_current_line: Parser[PARSE_RESULT]) -> Parser[PARSE_RESULT]:
        return CurrentLineMustNotBeEmptyExceptForSpace(
            with_non_empty_current_line,
            'Missing ' + element_name,
        )

    def parse(self, source: ParseSource) -> PARSE_RESULT:
        if source.is_at_eol__except_for_space:
            raise instruction_parser_exceptions.SingleInstructionInvalidArgumentException(
                self._error_message_if_current_line_empty
            )

        return self._with_non_empty_current_line.parse(source)

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        parser.require_is_not_at_eol(self._error_message_if_current_line_empty)
        return self._with_non_empty_current_line.parse_from_token_parser(parser)


def parser_for_must_be_on_current_line(grammar: Grammar[EXPR],
                                       any_line_parser: Parser[EXPR],
                                       must_be_on_current_line: bool = True,
                                       ) -> Parser[EXPR]:
    return (
        CurrentLineMustNotBeEmptyExceptForSpace(
            any_line_parser,
            'Missing ' + grammar.concept.syntax_element.name
        )
        if must_be_on_current_line
        else
        any_line_parser
    )
