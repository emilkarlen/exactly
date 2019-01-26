from typing import Generic

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser, PARSE_RESULT


class ConstantParser(Generic[PARSE_RESULT], Parser[PARSE_RESULT]):
    """Parser with constant result, which does not consume any source."""

    def __init__(self, result: PARSE_RESULT):
        super().__init__()
        self._result = result

    def parse(self, source: ParseSource) -> PARSE_RESULT:
        return self._result

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        return self._result
