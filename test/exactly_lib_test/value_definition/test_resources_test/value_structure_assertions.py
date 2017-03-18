import unittest

from exactly_lib.util.line_source import Line
from exactly_lib.value_definition.concrete_restrictions import NoRestriction, FileRefRelativityRestriction
from exactly_lib.value_definition.concrete_values import StringValue, FileRefValue
from exactly_lib.value_definition.value_structure import ValueContainer, ValueReference2
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_structure_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsValueContainer),
        unittest.makeSuite(TestEqualsValueReference),
    ])


class TestEqualsValueContainer(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            StringValue('s'),
            FileRefValue(file_ref_test_impl('file-name')),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    value_container = ValueContainer(Line(1, 'source code'), value)
                    assertion = sut.equals_value_container(value_container, ignore_source_line=ignore_source_line)
                    # ACT #
                    assertion.apply_without_message(self, value_container)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value = StringValue('common string value')
        expected = ValueContainer(Line(4, 'source code 4'), common_value)
        actual = ValueContainer(Line(5, 'source code 5'), common_value)
        put = test_case_with_failure_exception_set_to_test_exception()
        sut.equals_value_container(expected, ignore_source_line=True).apply_without_message(put, actual)

    def test_fail__different_source_line_and_source_line_check_is_not_ignored(self):
        # ARRANGE #
        common_value = FileRefValue(file_ref_test_impl('common file-name'))
        expected = ValueContainer(Line(1, 'source code 1'), common_value)
        actual = ValueContainer(Line(2, 'source code 2'), common_value)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_value_container(expected, ignore_source_line=False).apply_without_message(put, actual)


class TestEqualsValueReference(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        value_name = 'value name'
        value_reference = ValueReference2(value_name, NoRestriction())
        assertion = sut.equals_value_reference(value_name, asrt.is_instance(NoRestriction))
        # ACT & ASSERT #
        assertion.apply_without_message(self, value_reference)

    def test_fail__different_name(self):
        # ARRANGE #
        actual = ValueReference2('actual value name', NoRestriction())
        assertion = sut.equals_value_reference('expected value name', asrt.is_instance(NoRestriction))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_fail__failing_assertion_on_value_restriction(self):
        # ARRANGE #
        common_name = 'actual value name'
        actual = ValueReference2(common_name, NoRestriction())
        assertion = sut.equals_value_reference(common_name, asrt.is_instance(FileRefRelativityRestriction))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)
