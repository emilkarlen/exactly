from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher, combinator_sdvs
from exactly_lib.test_case_utils.string_matcher.impl import line_matches
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.util.logic_types import ExpectationType, Quantifier


def parse(quantifier: Quantifier,
          expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(
        combinator_sdvs.of_expectation_type(
            parse__generic(quantifier, token_parser),
            expectation_type
        )
    )


def parse__all(parser: TokenParser) -> GenericStringMatcherSdv:
    return parse__generic(Quantifier.ALL, parser)


def parse__exists(parser: TokenParser) -> GenericStringMatcherSdv:
    return parse__generic(Quantifier.EXISTS, parser)


def parse__generic(quantifier: Quantifier,
                   token_parser: TokenParser) -> GenericStringMatcherSdv:
    return parse_quantified_matcher.parse_after_quantifier_token(
        quantifier,
        parse_line_matcher.ParserOfGenericMatcherOnArbitraryLine(),
        line_matches.ELEMENT_SETUP,
        token_parser
    )
