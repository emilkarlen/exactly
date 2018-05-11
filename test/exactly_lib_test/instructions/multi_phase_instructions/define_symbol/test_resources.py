from exactly_lib.definitions import file_ref
from exactly_lib.definitions.entity import types
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.resolver_structure import SymbolContainer, SymbolValueResolver
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, HARD_QUOTE_CHAR
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source, ParseSourceBuilder


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
    'lines_trans_type': types.STRING_TRANSFORMER_TYPE_INFO.identifier,
    'program_type': types.PROGRAM_TYPE_INFO.identifier,
    'soft_quote': SOFT_QUOTE_CHAR,
    'hard_quote': HARD_QUOTE_CHAR,
    'rel_tmp': file_ref.REL_TMP_OPTION,
    'rel_act': file_ref.REL_ACT_OPTION,
    'rel_result': file_ref.REL_RESULT_OPTION,
    'rel_cd': file_ref.REL_CWD_OPTION,
    'rel_home': file_ref.REL_HOME_CASE_OPTION,
    'rel_act_home': file_ref.REL_HOME_ACT_OPTION,
    'rel_symbol': file_ref.REL_symbol_OPTION,
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
    return SymbolContainer(value_resolver,
                           single_line_sequence(1, 'source line'))


SB = ParseSourceBuilder(_STD_FORMAT_MAP)
