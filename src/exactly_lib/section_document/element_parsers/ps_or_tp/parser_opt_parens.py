from typing import Generic

from exactly_lib.section_document.element_parsers import error_messages
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser, PARSE_RESULT
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.parse import token_matchers


class OptionallySurroundedByParenthesisParser(Generic[PARSE_RESULT], ParserFromTokenParserBase[PARSE_RESULT]):
    """"Parses a value that may be surrounded by parenthesis or not.

    Reports error by raising SingleInstructionInvalidArgumentException.
    """

    _IS_PAREN_BEGIN = token_matchers.is_unquoted_and_equals('(')
    _MISSING_PAREN_END = error_messages.ConstantErrorMessage("Missing ')' (unquoted)")

    def __init__(self, parser_of_plain: Parser[PARSE_RESULT]):
        """
        :param parser_of_plain: Parses without parenthesis
        """
        super().__init__(False, False)
        self._parser_of_plain = parser_of_plain

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        if parser.has_valid_head_token() and self._IS_PAREN_BEGIN.matches(parser.head):
            return self._parse_w_present_begin_paren(parser)
        else:
            return self._parser_of_plain.parse_from_token_parser(parser)

    def _parse_w_present_begin_paren(self, parser: TokenParser) -> PARSE_RESULT:
        parser.consume_head()
        ret_val = self._parser_of_plain.parse_from_token_parser(parser)
        parser.require_head_is_unquoted_and_equals(')', self._MISSING_PAREN_END)
        parser.consume_head()
        return ret_val
