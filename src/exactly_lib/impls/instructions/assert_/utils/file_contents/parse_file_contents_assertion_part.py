from exactly_lib.impls.instructions.assert_.utils import assertion_part
from exactly_lib.impls.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.impls.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.impls.instructions.assert_.utils.file_contents.parts.contents_checkers import \
    ConstructFileToCheckAssertionPart
from exactly_lib.impls.instructions.assert_.utils.file_contents.parts.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.impls.types.string_matcher.parse_string_matcher import parsers
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_prims.string_source.string_source import StringSource


def parse(token_parser: TokenParser) -> AssertionPart[ComparisonActualFile, StringSource]:
    string_matcher_sdv = parsers().full.parse_from_token_parser(token_parser)
    return assertion_part.compose(ConstructFileToCheckAssertionPart(),
                                  StringMatcherAssertionPart(string_matcher_sdv))
