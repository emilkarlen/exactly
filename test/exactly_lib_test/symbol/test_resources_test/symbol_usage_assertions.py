import unittest

import exactly_lib_test.symbol.test_resources.symbol_usage_assertions
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.restrictions import reference_restrictions as r, value_restrictions as vr
from exactly_lib.symbol.resolver_structure import container_of_builtin
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesDefinition),
        unittest.makeSuite(TestMatchesReference),
        unittest.makeSuite(TestMatchesReference2),
    ])


class TestMatchesDefinition(unittest.TestCase):
    def test_name_SHOULD_be_given_as_argument_to_assertion_on_name(self):
        # ARRANGE #
        actual_name = 'the name'
        actual_definition = SymbolDefinition(actual_name,
                                             container_of_builtin(string_resolvers.str_constant('s')))

        assertion_that_is_expected_to_succeed = asrt.is_(actual_name)

        assertion_to_check = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_definition(
            name=assertion_that_is_expected_to_succeed,
            container=asrt.anything_goes())
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_definition)

    def test_container_SHOULD_be_given_as_argument_to_assertion_on_container(self):
        # ARRANGE #
        actual_container = container_of_builtin(string_resolvers.str_constant('s'))
        actual_definition = SymbolDefinition('the name',
                                             actual_container)

        assertion_that_is_expected_to_succeed = asrt.is_(actual_container)

        assertion_to_check = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_definition(
            name=asrt.anything_goes(),
            container=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_definition)

    def test_arbitrary_failure(self):
        # ARRANGE #
        actual_container = container_of_builtin(string_resolvers.str_constant('s'))
        actual_definition = SymbolDefinition('the name',
                                             actual_container)

        assertion_that_is_expected_to_succeed = asrt.not_(asrt.is_(actual_container))

        assertion_to_check = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_definition(
            name=asrt.anything_goes(),
            container=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, actual_definition)


class TestMatchesReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(
                                               vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference(
            asrt.is_(symbol_name),
            asrt.is_instance(r.ReferenceRestrictionsOnDirectAndIndirect))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_pass_with_default_assertion_on_restrictions(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(
                                               vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference(
            asrt.is_(symbol_name))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name',
                                 r.ReferenceRestrictionsOnDirectAndIndirect(
                                     vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference(
            asrt.equals('expected value name'),
            asrt.anything_goes())
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        actual_symbol_name = 'actual value name'
        actual = SymbolReference(actual_symbol_name,
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference(
            assertion_on_restrictions=asrt.is_instance(r.OrReferenceRestrictions))
        assert_that_assertion_fails(assertion, actual)


class TestMatchesReference2(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(
                                               vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference_2(symbol_name,
                                                                                                       asrt.is_instance(
                                                                                                           r.ReferenceRestrictionsOnDirectAndIndirect))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_pass_with_default_assertion_on_restrictions(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = SymbolReference(symbol_name,
                                           r.ReferenceRestrictionsOnDirectAndIndirect(
                                               vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference_2(symbol_name)
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = SymbolReference('actual value name',
                                 r.ReferenceRestrictionsOnDirectAndIndirect(
                                     vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference_2(
            'expected value name',
            asrt.anything_goes())
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        actual_symbol_name = 'actual value name'
        actual = SymbolReference(actual_symbol_name,
                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.AnyDataTypeRestriction()))
        assertion = exactly_lib_test.symbol.test_resources.symbol_usage_assertions.matches_reference_2(
            actual_symbol_name,
            asrt.is_instance(r.OrReferenceRestrictions))
        assert_that_assertion_fails(assertion, actual)
