import unittest

from exactly_lib.impls.types.matcher.impls import constant as sut
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.test_resources.std_type_visitor import MatcherStdTypeVisitorTestAcceptImpl, \
    assert_argument_satisfies__and_return
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestConstant)


class TestConstant(unittest.TestCase):
    def test_application(self):
        cases = [
            NEA('constant true should match',
                True,
                True,
                ),
            NEA('constant false should not match',
                False,
                False,
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                matcher = sut.MatcherWithConstantResult(case.actual)
                # ACT #
                actual_result = matcher.matches_w_trace(None)

                # ASSERT #

                asrt_matching_result.matches_value(case.expected).apply_with_message(self,
                                                                                     actual_result,
                                                                                     'matching result')

    def test_accept_SHOULD_invoke_method_for_constant_matcher(self):
        const_value = False
        matcher = sut.MatcherWithConstantResult(const_value)
        return_value = 5
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            constant_action=assert_argument_satisfies__and_return(self, asrt.equals(const_value), return_value)
        )
        # ACT & ASSERT #
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')
