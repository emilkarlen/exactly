from exactly_lib.instructions.assert_.utils import assertion_part
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import \
    ComparisonActualFile, ConstructFileToCheckAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.string_matcher.parse import parse_string_matcher
from exactly_lib.type_system.logic.string_matcher import FileToCheck


def parse(token_parser: TokenParser) -> AssertionPart[ComparisonActualFile, FileToCheck]:
    string_matcher_resolver = parse_string_matcher.parse_string_matcher(token_parser)
    return assertion_part.compose(ConstructFileToCheckAssertionPart(),
                                  StringMatcherAssertionPart(string_matcher_resolver))
