from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.matcher.impls import comparison_matcher
from exactly_lib.type_system.logic.integer_matcher import IntegerMatcher
from exactly_lib.util.description_tree import details


def matcher(comparator: comparators.ComparisonOperator,
            rhs: int) -> IntegerMatcher:
    return comparison_matcher.ComparisonMatcher(
        syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
        comparator,
        rhs,
        lambda x: details.String(x),
    )
