from exactly_lib.instructions.assert_.utils import assertion_part
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import \
    ConstructFileToCheckAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.string_matcher import FileToCheck


def parse(token_parser: TokenParser) -> AssertionPart[ComparisonActualFile, FileToCheck]:
    string_matcher_sdv = parse_string_matcher.parse_string_matcher(token_parser)
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return assertion_part.compose(ConstructFileToCheckAssertionPart(),
                                  StringMatcherAssertionPart(string_matcher_sdv))
