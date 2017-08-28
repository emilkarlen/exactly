import unittest

from exactly_lib.named_element.restriction import ElementTypeRestriction
from exactly_lib.named_element.symbol.restrictions import reference_restrictions
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib_test.named_element.test_resources import restrictions_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsElementTypeRestriction),
    ])


class TestIsElementTypeRestriction(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        expected_type = ElementType.FILE_SELECTOR

        assertion_to_check = sut.is_element_type_restriction(expected_type)

        restriction = ElementTypeRestriction(expected_type)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, restriction)

    def test_fail_WHEN_element_type_is_unexpected(self):
        # ARRANGE #
        expected_type = ElementType.FILE_SELECTOR
        actual_type = ElementType.SYMBOL

        assertion_to_check = sut.is_element_type_restriction(expected_type)

        restriction = ElementTypeRestriction(actual_type)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)

    def test_fail_WHEN_restriction_is_of_other_type(self):
        # ARRANGE #
        assertion_to_check = sut.is_element_type_restriction(ElementType.SYMBOL)

        restriction = reference_restrictions.no_restrictions()
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)
