from typing import Optional

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.condition.integer.integer_value import CustomIntegerValidator
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    parse_integer_comparison_operator_and_rhs
from exactly_lib.test_case_utils.matcher.impls.comparison_matcher import ComparisonMatcherResolver
from exactly_lib.test_case_utils.matcher.impls.operand_object import ObjectResolverOfOperandResolver
from exactly_lib.test_case_utils.matcher.matcher import MatcherResolver
from exactly_lib.util.logic_types import ExpectationType


def parse(parser: TokenParser,
          expectation_type: ExpectationType,
          custom_integer_restriction: Optional[CustomIntegerValidator],
          ) -> MatcherResolver[int]:
    op_and_rhs = parse_integer_comparison_operator_and_rhs(parser,
                                                           custom_integer_restriction)
    return ComparisonMatcherResolver(
        expectation_type,
        op_and_rhs.operator,
        ObjectResolverOfOperandResolver(op_and_rhs.right_operand),
        str
    )
