from typing import Optional, List

import exactly_lib.definitions.primitives.file_matcher
from exactly_lib.definitions import expression
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.parse import token


def file_matcher_arguments(name_pattern: str = '',
                           type_match: FileType = None,
                           named_matcher: str = '',
                           contents_string_matcher: Optional[str] = None,
                           ) -> str:
    """
    Gives the CLI argument and options for the given matchers

    :param named_matcher: A named (reference to a) selector
    :param name_pattern: Name selector, or nothing, if empty string.
    :param type_match: Type selector, or nothing, if None
    :returns str: Empty string iff no selector is given.
    """
    matchers = []

    if name_pattern:
        matchers.append(name_glob_pattern_matcher_of(name_pattern))
    if type_match:
        matchers.append(type_matcher_of(type_match))
    if named_matcher:
        matchers.append(named_matcher)
    if contents_string_matcher:
        matchers.append(contents_matcher_of(contents_string_matcher))

    and_combinator = ' ' + expression.AND_OPERATOR_NAME + ' '
    return and_combinator.join(matchers)


def name_glob_pattern_matcher_of(pattern: str) -> str:
    pattern_arg = pattern
    if ' ' in pattern_arg and pattern_arg[0] not in token.QUOTE_CHARS:
        pattern_arg = token.HARD_QUOTE_CHAR + pattern_arg + token.HARD_QUOTE_CHAR

    return exactly_lib.definitions.primitives.file_matcher.NAME_MATCHER_NAME + ' ' + pattern_arg


def name_reg_ex_pattern_matcher_of(pattern: str,
                                   ignore_case: bool = False) -> str:
    pattern_arg = pattern
    if ' ' in pattern_arg and pattern_arg[0] not in token.QUOTE_CHARS:
        pattern_arg = token.HARD_QUOTE_CHAR + pattern_arg + token.HARD_QUOTE_CHAR

    args = [
        exactly_lib.definitions.primitives.file_matcher.NAME_MATCHER_NAME,
        option_syntax.option_syntax(parse_file_matcher.REG_EX_OPTION),
    ]
    if ignore_case:
        args.append(option_syntax.option_syntax(parse_regex.IGNORE_CASE_OPTION_NAME))

    args.append(pattern_arg)

    return ' '.join(args)


def and_(matchers: List[str]) -> str:
    and_combinator = ' ' + expression.AND_OPERATOR_NAME + ' '
    return and_combinator.join(matchers)


def type_matcher_of(file_type: file_properties.FileType) -> str:
    return exactly_lib.definitions.primitives.file_matcher.TYPE_MATCHER_NAME + \
           ' ' + \
           file_properties.TYPE_INFO[file_type].type_argument


def contents_matcher_of(string_matcher: str) -> str:
    return parse_file_matcher.REGULAR_FILE_CONTENTS + ' ' + string_matcher


def arbitrary_value_on_single_line() -> str:
    return type_matcher_of(file_properties.FileType.DIRECTORY)
