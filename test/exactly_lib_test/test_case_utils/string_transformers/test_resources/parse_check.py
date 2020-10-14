from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib_test.test_case_utils.test_resources.parse_checker import parse_checker

PARSE_CHECKER__FULL = parse_checker(parse_string_transformer.parsers().full)

PARSE_CHECKER__SIMPLE = parse_checker(parse_string_transformer.parsers().simple)
