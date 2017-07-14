import unittest

from exactly_lib.symbol.restrictions import reference_restrictions as r
from exactly_lib.symbol.restrictions import value_restrictions as vr
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as sut
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesSymbolReference),
        unittest.makeSuite(TestEqualsSymbolReference),
    ])


class TestMatchesSymbolReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_symbol_reference(symbol_name,
                                                 asrt.is_instance(r.ReferenceRestrictionsOnDirectAndIndirect))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_pass_with_default_assertion_on_restrictions(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_symbol_reference(symbol_name)
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name',
                                 r.ReferenceRestrictionsOnDirectAndIndirect(
                                     vr.NoRestriction()))
        assertion = sut.matches_symbol_reference('expected value name',
                                                 asrt.anything_goes())
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        actual_symbol_name = 'actual value name'
        actual = SymbolReference(actual_symbol_name,
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_symbol_reference(actual_symbol_name,
                                                 asrt.is_instance(r.OrReferenceRestrictions))
        assert_that_assertion_fails(assertion, actual)


class TestEqualsSymbolReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'value name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target(symbol_name,
                                                                                  asrt.is_instance(
                                                                                      vr.NoRestriction))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name',
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target('expected value name',
                                                                                  asrt.is_instance(
                                                                                      vr.NoRestriction))
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        common_name = 'actual value name'
        actual = SymbolReference(common_name,
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.equals_symbol_reference_with_restriction_on_direct_target(
            common_name,
            asrt.is_instance(vr.FileRefRelativityRestriction))
        assert_that_assertion_fails(assertion, actual)
