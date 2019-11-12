from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.test_case_utils.line_matcher.impl import delegated
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherResolverFromParts
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, property_getters
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def parse(token_parser: TokenParser) -> LineMatcherResolver:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_resolver = parse_regex.parse_regex2(token_parser,
                                                           must_be_on_same_line=True)

    return resolver(regex_resolver)


def resolver(regex_resolver: RegexResolver) -> LineMatcherResolver:
    def get_value(symbols: SymbolTable) -> LineMatcherDdv:
        regex_ddv = regex_resolver.resolve(symbols)
        regex_matcher = matches_regex.MatchesRegexDdv(ExpectationType.POSITIVE, regex_ddv, False)
        return delegated.LineMatcherValueDelegatedToMatcher(property_matcher.PropertyMatcherDdv(
            regex_matcher,
            property_getters.PropertyGetterValueConstant(
                _PropertyGetter(),
            ),
        ))

    return LineMatcherResolverFromParts(
        regex_resolver.references,
        get_value,
    )


class _PropertyGetter(PropertyGetter[LineMatcherLine, str]):
    @property
    def name(self) -> Optional[str]:
        return None

    def get_from(self, model: LineMatcherLine) -> str:
        return model[1]
