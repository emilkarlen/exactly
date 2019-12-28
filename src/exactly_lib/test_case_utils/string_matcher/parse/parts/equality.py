from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.test_case_utils.parse import parse_here_doc_or_path
from exactly_lib.test_case_utils.string_matcher.impl import equality
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType

_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS = 'EXPECTED'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_path.CONFIGURATION


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(
        combinator_sdvs.of_expectation_type(
            parse__generic(token_parser),
            expectation_type
        )
    )


def parse__generic(token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
    token_parser.require_has_valid_head_token(_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS)
    expected_contents = parse_here_doc_or_path.parse_from_token_parser(
        token_parser,
        EXPECTED_FILE_REL_OPT_ARG_CONFIG,
        consume_last_here_doc_line=False)

    return equality.sdv__generic(expected_contents)
