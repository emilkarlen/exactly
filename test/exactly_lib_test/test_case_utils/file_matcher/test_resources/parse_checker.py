from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib_test.instructions.test_resources.parse_checker import Checker
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser

PARSE_CHECKER__FULL = Checker(
    ParserAsLocationAwareParser(parse_file_matcher.parsers().full)
)

PARSE_CHECKER__SIMPLE = Checker(
    ParserAsLocationAwareParser(parse_file_matcher.parsers().simple)
)
