import unittest

from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_val_deps.test_resources.any_ import restrictions_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestIsValueTypeRestriction)


class TestIsValueTypeRestriction(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        expected_type = ValueType.FILE_MATCHER

        assertion_to_check = sut.is_reference_restrictions__value_type__single(expected_type)

        restriction = ValueTypeRestriction.of_single(expected_type)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, restriction)

    def test_succeed__multi(self):
        # ARRANGE #
        expected_types = [ValueType.FILE_MATCHER, ValueType.STRING]

        assertion_to_check = sut.is_reference_restrictions__value_type(expected_types)

        restriction = ValueTypeRestriction(expected_types)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, restriction)

    def test_fail_WHEN_restriction_is_of_other_type(self):
        # ARRANGE #
        assertion_to_check = sut.is_reference_restrictions__value_type__single(ValueType.PATH)

        restriction = reference_restrictions.is_string__all_indirect_refs_are_strings()
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)

    def test_fail_WHEN_restriction_is_of_other_type__multi(self):
        # ARRANGE #
        assertion_to_check = sut.is_reference_restrictions__value_type([ValueType.PATH, ValueType.PROGRAM])

        restriction = reference_restrictions.is_string__all_indirect_refs_are_strings()
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, restriction)
