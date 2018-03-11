from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.data import string_resolver as sr, list_resolver as lr
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.util.parse.token import Token


def parse_list(source: ParseSource) -> ListResolver:
    with from_parse_source(source) as token_parser:
        return parse_list_from_token_parser(token_parser)


def parse_list_from_token_parser(token_parser: TokenParser) -> ListResolver:
    return ListResolver(_consume_elements_from_token_parser(token_parser))


def _consume_elements_from_token_parser(token_parser: TokenParser) -> list:
    elements = []

    while not token_parser.is_at_eol:
        next_token = token_parser.consume_mandatory_token('Invalid list element')
        elements.append(element_of(next_token))

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
