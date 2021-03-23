from typing import List

from exactly_lib.definitions import path
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, HARD_QUOTE_CHAR
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source, ParseSourceBuilder


def src(s: str,
        **kwargs) -> str:
    if not kwargs:
        return s.format_map(_STD_FORMAT_MAP)
    else:
        formats = dict(_STD_FORMAT_MAP, **kwargs)
        return s.format_map(formats)


def src2(type_: ValueType,
         symbol_name: str,
         value_template: str,
         **kwargs) -> str:
    format_map = _STD_FORMAT_MAP
    if kwargs:
        format_map = dict(_STD_FORMAT_MAP, **kwargs)

    return src__const(type_,
                      symbol_name,
                      value_template.format_map(format_map))


def src3(type_: ValueType,
         symbol_name: str,
         value: str) -> str:
    return src__const(type_,
                      symbol_name,
                      value)


def src__const(type_: ValueType,
               symbol_name: str,
               value: str) -> str:
    return ' '.join([ANY_TYPE_INFO_DICT[type_].identifier,
                     symbol_name,
                     reserved_words.ASSIGN,
                     value])


_STD_FORMAT_MAP = {
    'path_type': types.PATH_TYPE_INFO.identifier,
    'string_type': types.STRING_TYPE_INFO.identifier,
    'list_type': types.LIST_TYPE_INFO.identifier,
    'line_match_type': types.LINE_MATCHER_TYPE_INFO.identifier,
    'string_matcher_type': types.STRING_MATCHER_TYPE_INFO.identifier,
    'file_matcher_type': types.FILE_MATCHER_TYPE_INFO.identifier,
    'files_matcher_type': types.FILES_MATCHER_TYPE_INFO.identifier,
    'string_trans_type': types.STRING_TRANSFORMER_TYPE_INFO.identifier,
    'program_type': types.PROGRAM_TYPE_INFO.identifier,
    'soft_quote': SOFT_QUOTE_CHAR,
    'hard_quote': HARD_QUOTE_CHAR,
    'rel_tmp': path.REL_TMP_OPTION,
    'rel_act': path.REL_ACT_OPTION,
    'rel_result': path.REL_RESULT_OPTION,
    'rel_cd': path.REL_CWD_OPTION,
    'rel_home': path.REL_HDS_CASE_OPTION,
    'rel_act_home': path.REL_HDS_ACT_OPTION,
    'rel_symbol': path.REL_symbol_OPTION,
    'rel_source_file': path.REL_source_file_dir_OPTION,
    'new_line': '\n',
}


def single_line_source(s: str,
                       **kwargs) -> ParseSource:
    return remaining_source(src(s, **kwargs))


def arbitrary_string_source(s: str,
                            **kwargs) -> ParseSource:
    return remaining_source(src(s, **kwargs))


def multi_line_source(first_line: str,
                      following_lines: List[str],
                      **kwargs) -> ParseSource:
    return remaining_source(src(first_line, **kwargs),
                            [src(line, **kwargs) for line in following_lines])


SB = ParseSourceBuilder(_STD_FORMAT_MAP)
