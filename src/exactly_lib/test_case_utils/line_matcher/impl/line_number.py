from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher, property_getters
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetterResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.util.logic_types import ExpectationType
from . import delegated


def parse_line_number(parser: TokenParser) -> LineMatcherResolver:
    matcher = parse_integer_matcher.parse(
        parser,
        ExpectationType.POSITIVE,
        parse_integer_matcher.validator_for_non_negative,
    )
    return delegated.LineMatcherResolverDelegatedToMatcher(
        property_matcher.PropertyMatcherResolver(
            matcher,
            _operand_from_model_resolver(),
        ),
    )


def _operand_from_model_resolver() -> PropertyGetterResolver[LineMatcherLine, int]:
    return property_getters.PropertyGetterResolverConstant(
        property_getters.PropertyGetterValueConstant(
            _PropertyGetter(),
        )
    )


class _PropertyGetter(property_getters.PropertyGetter[LineMatcherLine, int]):
    NAME = ' '.join((line_matcher.LINE_NUMBER_MATCHER_NAME,
                     syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))

    @property
    def name(self) -> str:
        return self.NAME

    def get_from(self, model: LineMatcherLine) -> int:
        return model[0]
