import unittest

from exactly_lib.named_element.named_element_usage import NamedElementDefinition, NamedElementReference
from exactly_lib.named_element.resolver_structure import NamedElementContainer, container_of_builtin
from exactly_lib.named_element.symbol.restrictions import reference_restrictions as r, value_restrictions as vr
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.util.line_source import Line
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesContainer),
        unittest.makeSuite(TestMatchesDefinition),
        unittest.makeSuite(TestMatchesReference),
        unittest.makeSuite(TestMatchesReference2),
    ])


class TestMatchesContainer(unittest.TestCase):
    def test_resolver_SHOULD_be_given_as_argument_to_resolver_assertion(self):
        # ARRANGE #
        actual_resolver = string_constant('s')
        actual_container = container_of_builtin(actual_resolver)
        assertion_that_is_expected_to_succeed = asrt.is_(actual_resolver)
        assertion_to_check = sut.matches_container(assertion_that_is_expected_to_succeed,
                                                   assertion_on_source=asrt.anything_goes())
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_container)

    def test_source_line_SHOULD_be_given_as_argument_to_source_line_assertion(self):
        # ARRANGE #
        actual_resolver = string_constant('s')
        source_line = Line(1, 'source line')
        actual_container = NamedElementContainer(actual_resolver,
                                                 source_line)
        assertion_that_is_expected_to_succeed = asrt.is_(source_line)
        assertion_to_check = sut.matches_container(
            assertion_on_resolver=asrt.anything_goes(),
            assertion_on_source=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_container)

    def test_arbitrary_failure(self):
        # ARRANGE #
        actual_resolver = string_constant('s')
        source_line = Line(1, 'source line')
        actual_container = NamedElementContainer(actual_resolver,
                                                 source_line)
        assertion_that_is_expected_to_fail = asrt.is_(asrt.not_(source_line))
        assertion_to_check = sut.matches_container(
            assertion_on_resolver=asrt.anything_goes(),
            assertion_on_source=assertion_that_is_expected_to_fail)
        assert_that_assertion_fails(assertion_to_check, actual_container)


class TestMatchesDefinition(unittest.TestCase):
    def test_name_SHOULD_be_given_as_argument_to_assertion_on_name(self):
        # ARRANGE #
        actual_name = 'the name'
        actual_definition = NamedElementDefinition(actual_name,
                                                   container_of_builtin(string_constant('s')))

        assertion_that_is_expected_to_succeed = asrt.is_(actual_name)

        assertion_to_check = sut.matches_definition(
            assertion_on_name=assertion_that_is_expected_to_succeed,
            assertion_on_container=asrt.anything_goes())
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_definition)

    def test_container_SHOULD_be_given_as_argument_to_assertion_on_container(self):
        # ARRANGE #
        actual_container = container_of_builtin(string_constant('s'))
        actual_definition = NamedElementDefinition('the name',
                                                   actual_container)

        assertion_that_is_expected_to_succeed = asrt.is_(actual_container)

        assertion_to_check = sut.matches_definition(
            assertion_on_name=asrt.anything_goes(),
            assertion_on_container=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_definition)

    def test_arbitrary_failure(self):
        # ARRANGE #
        actual_container = container_of_builtin(string_constant('s'))
        actual_definition = NamedElementDefinition('the name',
                                                   actual_container)

        assertion_that_is_expected_to_succeed = asrt.not_(asrt.is_(actual_container))

        assertion_to_check = sut.matches_definition(
            assertion_on_name=asrt.anything_goes(),
            assertion_on_container=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, actual_definition)


class TestMatchesReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = NamedElementReference(symbol_name,
                                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_reference(asrt.is_(symbol_name),
                                          asrt.is_instance(r.ReferenceRestrictionsOnDirectAndIndirect))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_pass_with_default_assertion_on_restrictions(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = NamedElementReference(symbol_name,
                                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_reference(asrt.is_(symbol_name))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = NamedElementReference('actual value name',
                                       r.ReferenceRestrictionsOnDirectAndIndirect(
                                           vr.NoRestriction()))
        assertion = sut.matches_reference(asrt.equals('expected value name'),
                                          asrt.anything_goes())
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        actual_symbol_name = 'actual value name'
        actual = NamedElementReference(actual_symbol_name,
                                       r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_reference(assertion_on_restrictions=asrt.is_instance(r.OrReferenceRestrictions))
        assert_that_assertion_fails(assertion, actual)


class TestMatchesReference2(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = NamedElementReference(symbol_name,
                                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_reference_2(symbol_name,
                                            asrt.is_instance(r.ReferenceRestrictionsOnDirectAndIndirect))
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_pass_with_default_assertion_on_restrictions(self):
        # ARRANGE #
        symbol_name = 'symbol name'
        symbol_reference = NamedElementReference(symbol_name,
                                                 r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_reference_2(symbol_name)
        # ACT & ASSERT #
        assertion.apply_without_message(self, symbol_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = NamedElementReference('actual value name',
                                       r.ReferenceRestrictionsOnDirectAndIndirect(
                                           vr.NoRestriction()))
        assertion = sut.matches_reference_2('expected value name',
                                            asrt.anything_goes())
        assert_that_assertion_fails(assertion, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        actual_symbol_name = 'actual value name'
        actual = NamedElementReference(actual_symbol_name,
                                       r.ReferenceRestrictionsOnDirectAndIndirect(vr.NoRestriction()))
        assertion = sut.matches_reference_2(actual_symbol_name,
                                            asrt.is_instance(r.OrReferenceRestrictions))
        assert_that_assertion_fails(assertion, actual)
