from exactly_lib.impls.types.condition import comparators
from exactly_lib_test.impls.types.integer_matcher.test_resources.abstract_syntaxes import \
    IntegerMatcherComparisonAbsStx, IntegerMatcherNegationAbsStx
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import IntegerMatcherAbsStx


def of_op(operator: comparators.ComparisonOperator,
          operand: int) -> IntegerMatcherAbsStx:
    return IntegerMatcherComparisonAbsStx.of_cmp_op__str(
        operator,
        str(operand)
    )


def of_neg_op(operator: comparators.ComparisonOperator,
              operand: int) -> IntegerMatcherAbsStx:
    return IntegerMatcherNegationAbsStx(of_op(operator, operand))
