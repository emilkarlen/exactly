import unittest

from exactly_lib.symbol.data.restrictions import value_restrictions as vr, reference_restrictions as r
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib_test.symbol.data.test_resources import symbol_reference_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsSymbolReference),
    ])


class TestEqualsSymbolReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'value name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(
                                                     vr.AnySymbolTypeRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target(symbol_name,
                                                                                  asrt.is_instance(
                                                                                      vr.AnySymbolTypeRestriction))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name',
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.AnySymbolTypeRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target('expected value name',
                                                                                  asrt.is_instance(
                                                                                      vr.AnySymbolTypeRestriction))
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        common_name = 'actual value name'
        actual = SymbolReference(common_name,
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.AnySymbolTypeRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target(
            common_name,
            asrt.is_instance(vr.FileRefRelativityRestriction))
        assert_that_assertion_fails(assertion, actual)
