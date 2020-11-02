from exactly_lib.impls.types.file_matcher import parse_file_matcher
from exactly_lib_test.impls.types.test_resources.parse_checker import parse_checker

PARSE_CHECKER__FULL = parse_checker(parse_file_matcher.parsers().full)

PARSE_CHECKER__SIMPLE = parse_checker(parse_file_matcher.parsers().simple)
