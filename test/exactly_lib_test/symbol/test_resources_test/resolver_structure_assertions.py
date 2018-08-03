import unittest

from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.resolver_structure import SymbolContainer, container_of_builtin
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.symbol.test_resources import resolver_structure_assertions as sut
from exactly_lib_test.symbol.test_resources import symbol_utils  as su
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesContainer)


class TestMatchesContainer(unittest.TestCase):
    def test_resolver_SHOULD_be_given_as_argument_to_resolver_assertion(self):
        # ARRANGE #
        actual_resolver = string_resolvers.str_constant('s')
        actual_container = container_of_builtin(actual_resolver)
        assertion_that_is_expected_to_succeed = asrt.is_(actual_resolver)
        assertion_to_check = sut.matches_container(assertion_that_is_expected_to_succeed,
                                                   assertion_on_source=asrt.anything_goes())
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_container)

    def test_source_line_SHOULD_be_given_as_argument_to_source_line_assertion(self):
        # ARRANGE #
        actual_resolver = string_resolvers.str_constant('s')
        source_line = single_line_sequence(1, 'source line')
        actual_container = SymbolContainer(actual_resolver,
                                           su.source_info_for_line_sequence(source_line))
        assertion_that_is_expected_to_succeed = equals_line_sequence(source_line)
        assertion_to_check = sut.matches_container(
            assertion_on_resolver=asrt.anything_goes(),
            assertion_on_source=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_container)

    def test_arbitrary_failure(self):
        # ARRANGE #
        actual_resolver = string_resolvers.str_constant('s')
        source_line = single_line_sequence(1, 'source line')
        actual_container = SymbolContainer(actual_resolver,
                                           su.source_info_for_line_sequence(source_line))
        assertion_that_is_expected_to_fail = asrt.not_(equals_line_sequence(source_line))
        assertion_to_check = sut.matches_container(
            assertion_on_resolver=asrt.anything_goes(),
            assertion_on_source=assertion_that_is_expected_to_fail)
        assert_that_assertion_fails(assertion_to_check, actual_container)
