import unittest

from exactly_lib.symbol import concrete_restrictions as r
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsSymbolReference)


class TestEqualsSymbolReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        value_name = 'value name'
        symbol_reference = SymbolReference(value_name, r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target(value_name,
                                                                                  asrt.is_instance(r.NoRestriction))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name', r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target('expected value name',
                                                                                  asrt.is_instance(r.NoRestriction))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        common_name = 'actual value name'
        actual = SymbolReference(common_name, r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction()))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_symbol_reference_with_restriction_on_direct_target(common_name, asrt.is_instance(
                r.FileRefRelativityRestriction))
            assertion.apply_without_message(put, actual)
