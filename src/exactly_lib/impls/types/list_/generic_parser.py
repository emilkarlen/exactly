from typing import TypeVar, Generic, List

from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens, TokenParser
from exactly_lib.type_val_deps.types.list_ import defs

ELEMENT = TypeVar('ELEMENT')


class ElementsUntilEndOfLineParser(Generic[ELEMENT], ParserFromTokens[List[ELEMENT]]):
    def __init__(self, element_parser: ParserFromTokens[ELEMENT]):
        self._element_parser = element_parser

    def parse(self, token_parser: TokenParser) -> List[ELEMENT]:
        ret_val = []

        while not token_parser.is_at_eol:
            if token_parser.remaining_part_of_current_line.strip() == defs.CONTINUATION_TOKEN:
                token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
                continue
            if token_parser.has_valid_head_matching(defs.IS_STOP_AT_TOKEN):
                break
            ret_val.append(self._element_parser.parse(token_parser))

        if token_parser.is_at_eol:
            token_parser.consume_remaining_part_of_current_line_as_string()

        return ret_val
