from typing import Set

import exactly_lib.test_case_utils.condition.integer.integer_value
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_cmp_op
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcherFromComparisonOperator
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    IntegerComparisonOperatorAndRightOperandResolver
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import validator_for_non_negative
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherLineNumber
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherResolverFromParts
from exactly_lib.type_system.logic.line_matcher import LineMatcherValue, LineMatcher
from exactly_lib.util.symbol_table import SymbolTable


def parse_line_number(parser: TokenParser) -> LineMatcherResolver:
    cmp_op_and_rhs = parse_cmp_op.parse_integer_comparison_operator_and_rhs(parser,
                                                                            validator_for_non_negative)

    return resolver(cmp_op_and_rhs)


def resolver(condition: IntegerComparisonOperatorAndRightOperandResolver) -> LineMatcherResolver:
    def get_value(symbols: SymbolTable) -> LineMatcherValue:
        return _Value(condition.operator,
                      condition.right_operand.resolve(symbols))

    return LineMatcherResolverFromParts(
        condition.right_operand.references,
        get_value,
    )


class _Value(LineMatcherValue):
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 int_expression: exactly_lib.test_case_utils.condition.integer.integer_value.IntegerValue):
        self._operator = operator
        self._int_expression = int_expression

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._int_expression.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._int_expression.validator()

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._matcher_of(self._int_expression.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: HomeAndSds) -> LineMatcher:
        return self._matcher_of(self._int_expression.value_of_any_dependency(tcds))

    def _matcher_of(self, rhs: int) -> LineMatcher:
        return LineMatcherLineNumber(IntegerMatcherFromComparisonOperator(self._operator,
                                                                          rhs))
