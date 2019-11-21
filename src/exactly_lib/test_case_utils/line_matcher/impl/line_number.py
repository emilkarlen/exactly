from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher, property_getters
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetterSdv
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.util.logic_types import ExpectationType


def parse_line_number(parser: TokenParser) -> LineMatcherSdv:
    matcher = parse_integer_matcher.parse(
        parser,
        ExpectationType.POSITIVE,
        parse_integer_matcher.validator_for_non_negative,
    )
    return LineMatcherSdv(
        property_matcher.PropertyMatcherSdv(
            matcher,
            _operand_from_model_sdv(),
        ),
    )


def _operand_from_model_sdv() -> PropertyGetterSdv[LineMatcherLine, int]:
    return property_getters.PropertyGetterSdvConstant(
        property_getters.PropertyGetterValueConstant(
            _PropertyGetter(),
        )
    )


class _PropertyGetter(property_getters.PropertyGetter[LineMatcherLine, int]):
    NAME = ' '.join((line_matcher.LINE_NUMBER_MATCHER_NAME,
                     syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))

    @property
    def name(self) -> Optional[str]:
        return self.NAME

    def get_from(self, model: LineMatcherLine) -> int:
        return model[0]
