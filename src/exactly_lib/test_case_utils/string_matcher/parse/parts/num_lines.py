from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_getters, parse_integer_matcher
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterResolver
from exactly_lib.test_case_utils.string_matcher import delegated_matcher, matcher_options
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    matcher = parse_integer_matcher.parse(
        token_parser,
        expectation_type,
        parse_integer_matcher.validator_for_non_negative,
    )
    return delegated_matcher.StringMatcherResolverDelegatedToMatcher(
        property_matcher.PropertyMatcherResolver(
            matcher,
            _operand_from_model_resolver(),
        ),
    )


class _PropertyGetter(PropertyGetter[FileToCheck, int]):
    NAME = ' '.join((matcher_options.NUM_LINES_ARGUMENT,
                     syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))

    @property
    def name(self) -> Optional[str]:
        return self.NAME

    def get_from(self, model: FileToCheck) -> int:
        ret_val = 0
        with model.lines() as lines:
            for _ in lines:
                ret_val += 1
        return ret_val


def _operand_from_model_resolver() -> PropertyGetterResolver[FileToCheck, int]:
    return property_getters.PropertyGetterResolverConstant(
        property_getters.PropertyGetterValueConstant(
            _PropertyGetter(),
        )
    )
