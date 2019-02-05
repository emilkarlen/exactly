from typing import Set

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer import integer_resolver
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_cmp_op
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcherFromComparisonOperator
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    IntegerComparisonOperatorAndRightOperand
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import validator_for_non_negative
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherLineNumber
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherResolverFromParts
from exactly_lib.type_system.logic.line_matcher import LineMatcherValue, LineMatcher
from exactly_lib.util.symbol_table import SymbolTable

LINE_NUMBER_PROPERTY = 'line number'


def parse_line_number(parser: TokenParser) -> LineMatcherResolver:
    cmp_op_and_rhs = parse_cmp_op.parse_integer_comparison_operator_and_rhs(parser,
                                                                            validator_for_non_negative,
                                                                            LINE_NUMBER_PROPERTY)

    return resolver(cmp_op_and_rhs)


def resolver(condition: IntegerComparisonOperatorAndRightOperand) -> LineMatcherResolver:
    def get_value(symbols: SymbolTable) -> LineMatcherValue:
        return _Value(condition.right_operand.property_name,
                      condition.operator,
                      condition.right_operand.resolve(symbols))

    return LineMatcherResolverFromParts(
        condition.right_operand.references,
        get_value,
    )


class _Value(LineMatcherValue):
    def __init__(self,
                 name_of_lhs: str,
                 operator: comparators.ComparisonOperator,
                 int_expression: integer_resolver.IntegerValue):
        self._name_of_lhs = name_of_lhs
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
        return LineMatcherLineNumber(IntegerMatcherFromComparisonOperator(self._name_of_lhs,
                                                                          self._operator,
                                                                          rhs))
