from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
from exactly_lib.named_element.resolver_structure import NamedElementContainer, NamedElementResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.line_source import Line
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, HARD_QUOTE_CHAR
from exactly_lib_test.test_resources.parse import remaining_source


def src(s: str,
        **kwargs) -> str:
    if not kwargs:
        return s.format_map(_STD_FORMAT_MAP)
    else:
        formats = dict(_STD_FORMAT_MAP, **kwargs)
        return s.format_map(formats)


_STD_FORMAT_MAP = {
    'path_type': help_texts.PATH_TYPE,
    'string_type': help_texts.STRING_TYPE,
    'list_type': help_texts.LIST_TYPE,
    # 'file_sel_type': help_texts.FILE_SELECTOR_TYPE,
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


def resolver_container(value_resolver: NamedElementResolver) -> NamedElementContainer:
    return NamedElementContainer(value_resolver, Line(1, 'source line'))
