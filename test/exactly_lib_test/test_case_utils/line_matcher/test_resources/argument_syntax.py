from exactly_lib.test_case_utils.line_matcher import parse_line_matcher


def syntax_for_regex_matcher(regex_token_str: str) -> str:
    return ' '.join([
        parse_line_matcher.REGEX_MATCHER_NAME,
        regex_token_str,
    ])
