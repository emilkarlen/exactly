from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib_test.test_case_utils.test_resources.parse_checker import parse_checker

PARSE_CHECKER__FULL = parse_checker(parse_file_matcher.parsers().full)

PARSE_CHECKER__SIMPLE = parse_checker(parse_file_matcher.parsers().simple)
