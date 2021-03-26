from typing import TypeVar, Generic, List

from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens, TokenParser
from exactly_lib.symbol.sdv_structure import SymbolName
from exactly_lib.type_val_deps.types.list_ import defs
from exactly_lib.util import either
from exactly_lib.util.either import Either

ELEMENT = TypeVar('ELEMENT')
ELEMENT_PRIME = TypeVar('ELEMENT_PRIME')


class ElementsUntilEndOfLineParser2(Generic[ELEMENT], ParserFromTokens[List[ELEMENT]]):
    def __init__(self,
                 element_parser: ParserFromTokens[Either[SymbolName, ELEMENT_PRIME]],
                 mk_element: either.Reducer[SymbolName, ELEMENT_PRIME, ELEMENT],
                 ):
        self._element_parser = element_parser
        self._mk_element = mk_element

    def parse(self, token_parser: TokenParser) -> List[ELEMENT]:
        ret_val = []

        while not token_parser.is_at_eol:
            if token_parser.remaining_part_of_current_line.strip() == defs.CONTINUATION_TOKEN:
                token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
                continue
            if token_parser.has_valid_head_matching(defs.IS_STOP_AT_TOKEN):
                break
            sym_name_or_element = self._element_parser.parse(token_parser)
            ret_val.append(self._mk_element.reduce(sym_name_or_element))

        if token_parser.is_at_eol:
            token_parser.consume_remaining_part_of_current_line_as_string()

        return ret_val

    def _parse_element(self, token_parser: TokenParser) -> ELEMENT:
        return self._mk_element.reduce(self._element_parser.parse(token_parser))
