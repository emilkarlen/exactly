from typing import List

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, from_parse_source, \
    ParserFromTokens
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolName
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.types.list_ import list_sdvs as lrs
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util import either
from . import generic_parser

_STRING_ELEMENT_PARSE_CONFIGURATION = parse_string.Configuration(
    syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    reference_restrictions.is_any_type_w_str_rendering(),
)


def parse_list(source: ParseSource) -> ListSdv:
    with from_parse_source(source) as token_parser:
        return parse_list_from_token_parser(token_parser)


def parse_list_from_token_parser(token_parser: TokenParser) -> ListSdv:
    return lrs.from_elements(_consume_elements_from_token_parser(token_parser))


def _consume_elements_from_token_parser(token_parser: TokenParser) -> List[lrs.ElementSdv]:
    return _ELEMENT_SEQUENCE_PARSER.parse(token_parser)


class _MkElement(either.Reducer[SymbolName, StringSdv, lrs.ElementSdv]):
    def reduce_left(self, x: SymbolName) -> lrs.ElementSdv:
        return symbol_reference_element(x)

    def reduce_right(self, x: StringSdv) -> lrs.ElementSdv:
        return lrs.string_element(x)


_ELEMENT_SEQUENCE_PARSER: ParserFromTokens[List[lrs.ElementSdv]] = (
    generic_parser.ElementsUntilEndOfLineParser2(
        parse_string.SymbolReferenceOrStringParser(_STRING_ELEMENT_PARSE_CONFIGURATION),
        _MkElement(),
    )
)


def symbol_reference_element(s: str) -> lrs.ElementSdv:
    return lrs.symbol_element(_symbol_reference(s))


def _symbol_reference(symbol_name: str) -> SymbolReference:
    return SymbolReference(
        symbol_name,
        reference_restrictions.is_any_type_w_str_rendering(),
    )
