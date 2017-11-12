from exactly_lib.help_texts.entity import types
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.resolver_structure import SymbolContainer, SymbolValueResolver
from exactly_lib.util.line_source import Line
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, HARD_QUOTE_CHAR
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source


def src(s: str,
        **kwargs) -> str:
    if not kwargs:
        return s.format_map(_STD_FORMAT_MAP)
    else:
        formats = dict(_STD_FORMAT_MAP, **kwargs)
        return s.format_map(formats)


_STD_FORMAT_MAP = {
    'path_type': types.PATH_TYPE_INFO.identifier,
    'string_type': types.STRING_TYPE_INFO.identifier,
    'list_type': types.LIST_TYPE_INFO.identifier,
    'line_match_type': types.LINE_MATCHER_TYPE_INFO.identifier,
    'file_matcher_type': types.FILE_MATCHER_TYPE_INFO.identifier,
    'lines_trans_type': types.LINES_TRANSFORMER_TYPE_INFO.identifier,
    'soft_quote': SOFT_QUOTE_CHAR,
    'hard_quote': HARD_QUOTE_CHAR,
}


def single_line_source(s: str,
                       **kwargs) -> ParseSource:
    return remaining_source(src(s, **kwargs))


def multi_line_source(first_line: str,
                      following_lines: list,
                      **kwargs) -> ParseSource:
    return remaining_source(src(first_line, **kwargs),
                            [src(line, **kwargs) for line in following_lines])


def resolver_container(value_resolver: SymbolValueResolver) -> SymbolContainer:
    return SymbolContainer(value_resolver, Line(1, 'source line'))
