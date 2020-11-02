import unittest

from exactly_lib.impls.types.matcher.impls import combinator_matchers as sut
from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.test_resources.std_type_visitor import \
    MatcherStdTypeVisitorTestAcceptImpl, assert_argument_satisfies__and_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNegation),
        unittest.makeSuite(TestConjunction),
        unittest.makeSuite(TestDisjunction),
    ])


class TestNegation(unittest.TestCase):
    def test_accept_visitor_invokes_correct_method(self):
        # ARRANGE #
        operand = constant.MatcherWithConstantResult(False)
        matcher = sut.Negation(operand)

        return_value = 5
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            negation_action=assert_argument_satisfies__and_return(self, asrt.is_(operand), return_value)
        )
        # ACT & ASSERT #
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')


class TestConjunction(unittest.TestCase):
    def test_accept_visitor_invokes_correct_method(self):
        # ARRANGE #
        operand1 = constant.MatcherWithConstantResult(False)
        operand2 = constant.MatcherWithConstantResult(False)
        operand3 = constant.MatcherWithConstantResult(False)
        matcher = sut.Conjunction([operand1, operand2, operand3])

        return_value = 7
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            conjunction_action=assert_argument_satisfies__and_return(
                self,
                asrt.matches_sequence([asrt.is_(operand1), asrt.is_(operand2), asrt.is_(operand3)]),
                return_value,
            )
        )
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')


class TestDisjunction(unittest.TestCase):
    def test_accept_visitor_invokes_correct_method(self):
        # ARRANGE #
        operand1 = constant.MatcherWithConstantResult(False)
        operand2 = constant.MatcherWithConstantResult(False)
        matcher = sut.Disjunction([operand1, operand2])

        return_value = 11
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            disjunction_action=assert_argument_satisfies__and_return(
                self,
                asrt.matches_sequence([asrt.is_(operand1), asrt.is_(operand2)]),
                return_value,
            )
        )
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
