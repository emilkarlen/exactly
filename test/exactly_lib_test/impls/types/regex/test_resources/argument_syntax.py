from typing import List

from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.parse import token


def reg_ex_args_list(pattern: str, ignore_case: bool = False) -> List[str]:
    pattern_arg = pattern
    if ' ' in pattern_arg and pattern_arg[0] not in token.QUOTE_CHARS:
        pattern_arg = token.HARD_QUOTE_CHAR + pattern_arg + token.HARD_QUOTE_CHAR

    args = []
    if ignore_case:
        args.append(option_syntax.option_syntax(parse_regex.IGNORE_CASE_OPTION_NAME))

    args.append(pattern_arg)

    return args
