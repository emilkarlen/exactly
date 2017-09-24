import unittest

from exactly_lib.symbol.data.restrictions import reference_restrictions
from exactly_lib.symbol.restriction import TypeCategoryRestriction, ValueTypeRestriction
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib_test.symbol.test_resources import restrictions_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsElementTypeRestriction),
        unittest.makeSuite(TestIsValueTypeRestriction),
    ])


class TestIsElementTypeRestriction(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        expected_type = TypeCategory.LOGIC

        assertion_to_check = sut.is_type_category_restriction(expected_type)

        restriction = TypeCategoryRestriction(expected_type)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, restriction)

    def test_fail_WHEN_type_category_is_unexpected(self):
        # ARRANGE #
        expected_type = TypeCategory.LOGIC
        actual_type = TypeCategory.DATA

        assertion_to_check = sut.is_type_category_restriction(expected_type)

        restriction = TypeCategoryRestriction(actual_type)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)

    def test_fail_WHEN_restriction_is_of_other_type(self):
        # ARRANGE #
        assertion_to_check = sut.is_type_category_restriction(TypeCategory.DATA)

        restriction = reference_restrictions.is_any_data_type()
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)


class TestIsValueTypeRestriction(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        expected_type = ValueType.FILE_MATCHER

        assertion_to_check = sut.is_value_type_restriction(expected_type)

        restriction = ValueTypeRestriction(expected_type)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, restriction)

    def test_fail_WHEN_type_category_is_unexpected(self):
        # ARRANGE #
        expected_type = ValueType.STRING
        actual_type = ValueType.FILE_MATCHER

        assertion_to_check = sut.is_value_type_restriction(expected_type)

        restriction = ValueTypeRestriction(actual_type)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)

    def test_fail_WHEN_restriction_is_of_other_type(self):
        # ARRANGE #
        assertion_to_check = sut.is_value_type_restriction(ValueType.PATH)

        restriction = reference_restrictions.is_any_data_type()
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)
