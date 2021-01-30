from exactly_lib.impls.types.string_transformer import parse_string_transformer
from exactly_lib_test.impls.types.test_resources.parse_checker import parse_checker

PARSE_CHECKER__FULL = parse_checker(parse_string_transformer.parsers().full)

PARSE_CHECKER__SIMPLE = parse_checker(parse_string_transformer.parsers().simple)
