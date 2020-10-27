import unittest

from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.matcher.impls import comparison_matcher as sut
from exactly_lib.util.description_tree import details
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.std_type_visitor import MatcherStdTypeVisitorTestAcceptImpl, \
    assert_argument_satisfies__and_return


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestComparisonMatcher)


class TestComparisonMatcher(unittest.TestCase):
    def test_accept_SHOULD_invoke_method_for_non_standard_matcher(self):
        return_value = 5
        for comparator in comparators.ALL_OPERATORS:
            with self.subTest(comparator.name):
                the_matcher = sut.ComparisonMatcher(
                    sut.Config(
                        'SYNTAX-ELEMENT',
                        comparator,
                        lambda model: details.empty()),
                    1,
                )
                visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
                    non_standard_action=assert_argument_satisfies__and_return(self, asrt.is_(the_matcher),
                                                                              return_value)
                )
                # ACT & ASSERT #
                actual_return_value = the_matcher.accept(visitor)
                # ASSERT #
                self.assertEqual(return_value, actual_return_value, 'return value')
