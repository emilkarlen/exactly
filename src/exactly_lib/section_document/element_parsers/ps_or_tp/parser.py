from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource

PARSE_RESULT = TypeVar('PARSE_RESULT')


class Parser(Generic[PARSE_RESULT], ABC):
    @abstractmethod
    def parse(self, source: ParseSource) -> PARSE_RESULT:
        pass

    @abstractmethod
    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        pass
