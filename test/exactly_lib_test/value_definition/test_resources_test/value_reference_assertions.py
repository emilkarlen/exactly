import unittest

from exactly_lib.value_definition.concrete_restrictions import NoRestriction, FileRefRelativityRestriction
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_reference_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsValueReference)


class TestEqualsValueReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        value_name = 'value name'
        value_reference = ValueReference(value_name, NoRestriction())
        assertion = sut.equals_value_reference(value_name, asrt.is_instance(NoRestriction))
        # ACT & ASSERT #
        assertion.apply_without_message(self, value_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = ValueReference('actual value name', NoRestriction())
        assertion = sut.equals_value_reference('expected value name', asrt.is_instance(NoRestriction))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        common_name = 'actual value name'
        actual = ValueReference(common_name, NoRestriction())
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_value_reference(common_name, asrt.is_instance(FileRefRelativityRestriction))
            assertion.apply_without_message(put, actual)
