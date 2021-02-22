import unittest

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions as r, value_restrictions as vr
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.data import symbol_reference_assertions as sut


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
                                               vr.AnyDataTypeRestriction()))
        assertion = sut.matches_symbol_reference_with_restriction_on_direct_target(symbol_name,
                                                                                   asrt.is_instance(
                                                                                       vr.AnyDataTypeRestriction))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name',
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.AnyDataTypeRestriction()))
        assertion = sut.matches_symbol_reference_with_restriction_on_direct_target('expected value name',
                                                                                   asrt.is_instance(
                                                                                       vr.AnyDataTypeRestriction))
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        common_name = 'actual value name'
        actual = SymbolReference(common_name,
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.AnyDataTypeRestriction()))
        assertion = sut.matches_symbol_reference_with_restriction_on_direct_target(
            common_name,
            asrt.is_instance(vr.PathRelativityRestriction))
        assert_that_assertion_fails(assertion, actual)
