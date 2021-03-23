from typing import List

from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.test_case import reserved_tokens
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, from_parse_source, \
    ParserFromTokens
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.types.list_ import list_sdvs as lrs
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.util.parse.token import Token
from . import generic_parser


def parse_list(source: ParseSource) -> ListSdv:
    with from_parse_source(source) as token_parser:
        return parse_list_from_token_parser(token_parser)


def parse_list_from_token_parser(token_parser: TokenParser) -> ListSdv:
    return lrs.from_elements(_consume_elements_from_token_parser(token_parser))


def _consume_elements_from_token_parser(token_parser: TokenParser) -> List[lrs.ElementSdv]:
    return _ELEMENT_SEQUENCE_PARSER.parse(token_parser)


class _ElementParser(ParserFromTokens[lrs.ElementSdv]):
    def parse(self, token_parser: TokenParser) -> lrs.ElementSdv:
        return parse_element(token_parser)


ELEMENT_PARSER: ParserFromTokens[lrs.ElementSdv] = _ElementParser()

_ELEMENT_SEQUENCE_PARSER: ParserFromTokens[List[lrs.ElementSdv]] = (
    generic_parser.ElementsUntilEndOfLineParser(ELEMENT_PARSER)
)


def parse_element(token_parser: TokenParser) -> lrs.ElementSdv:
    if not token_parser.has_valid_head_token():
        err_msg = 'Invalid list element: ' + repr(token_parser.remaining_part_of_current_line)
        raise SingleInstructionInvalidArgumentException(err_msg)
    if reserved_tokens.IS_RESERVED_WORD.matches(token_parser.head):
        err_msg = 'Invalid list element: {}: {}'.format(
            misc_texts.RESERVED_WORD_NAME,
            repr(token_parser.remaining_part_of_current_line),
        )
        raise SingleInstructionInvalidArgumentException(err_msg)

    return element_of(token_parser.consume_head())


def element_of(token: Token) -> lrs.ElementSdv:
    string_fragments = parse_string.parse_fragments_from_token(token)
    if len(string_fragments) == 1:
        single_fragment = string_fragments[0]
        if single_fragment.is_constant:
            return lrs.str_element(single_fragment.value)
        else:
            return symbol_reference_element(single_fragment.value)
    else:
        string_sdv = parse_string.string_sdv_from_fragments(
            string_fragments,
            reference_restrictions.is_any_type_w_str_rendering(),
        )
        return lrs.string_element(string_sdv)


def symbol_reference_element(s: str) -> lrs.ElementSdv:
    return lrs.symbol_element(_symbol_reference(s))


def _symbol_reference(symbol_name: str) -> SymbolReference:
    return SymbolReference(
        symbol_name,
        reference_restrictions.is_any_type_w_str_rendering(),
    )
