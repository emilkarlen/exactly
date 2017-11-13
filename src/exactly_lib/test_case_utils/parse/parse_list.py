from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse as tp
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.data import string_resolver as sr, list_resolver as lr
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.util.parse.token import Token


def parse_list_from_token_stream_that_consume_whole_source__TO_REMOVE(source: TokenStream) -> ListResolver:
    """
    Variant of parse_list that exists just so that can be used by the
    current design of the assign_symbol instruction.

    TODO Rewrite assign_symbol so that it uses a ParseSource for parsing!
    """
    ret_val = parse_list(ParseSource(source.remaining_source))
    while not source.is_null:
        source.consume()
    return ret_val


def parse_list(source: ParseSource) -> ListResolver:
    if source.is_at_eof:
        return ListResolver([])

    if source.is_at_eol__except_for_space:
        source.consume_current_line()
        return ListResolver([])

    elements = _consume_elements(source)
    if not source.is_at_eof:
        source.consume_current_line()
    return ListResolver(elements)


def _consume_elements(source: ParseSource) -> list:
    elements = []

    next_token = tp.parse_token_on_current_line(source)

    while next_token is not None:
        elements.append(element_of(next_token))
        next_token = tp.parse_token_or_none_on_current_line(source)

    return elements


def element_of(token: Token) -> lr.Element:
    string_fragments = parse_string.parse_fragments_from_token(token)
    if len(string_fragments) == 1:
        single_fragment = string_fragments[0]
        assert isinstance(single_fragment, symbol_syntax.Fragment)
        if single_fragment.is_constant:
            return _string_constant_element(single_fragment.value)
        else:
            return _symbol_reference_element(single_fragment.value)
    else:
        string_resolver = parse_string.string_resolver_from_fragments(string_fragments,
                                                                      is_any_data_type())
        return lr.StringResolverElement(string_resolver)


def _string_constant_element(s: str) -> lr.Element:
    return lr.StringResolverElement(sr.string_constant(s))


def _symbol_reference_element(s: str) -> lr.Element:
    return lr.SymbolReferenceElement(_symbol_reference(s))


def _symbol_reference(symbol_name: str) -> SymbolReference:
    return SymbolReference(symbol_name,
                           is_any_data_type())
