import unittest

from exactly_lib.util.line_source import Line
from exactly_lib.value_definition.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.value_definition.value_resolvers.string_resolvers import StringConstant
from exactly_lib.value_definition.value_structure import ValueContainer, ValueDefinition
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import value_structure_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsValueContainer),
        unittest.makeSuite(TestEqualsValueDefinition),
    ])


class TestEqualsValueContainer(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            StringConstant('s'),
            FileRefConstant(file_ref_test_impl('file-name')),
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
        common_value = StringConstant('common string value')
        expected = ValueContainer(Line(4, 'source code 4'), common_value)
        actual = ValueContainer(Line(5, 'source code 5'), common_value)
        put = test_case_with_failure_exception_set_to_test_exception()
        sut.equals_value_container(expected, ignore_source_line=True).apply_without_message(put, actual)

    def test_fail__different_source_line_and_source_line_check_is_not_ignored(self):
        # ARRANGE #
        common_value = FileRefConstant(file_ref_test_impl('common file-name'))
        expected = ValueContainer(Line(1, 'source code 1'), common_value)
        actual = ValueContainer(Line(2, 'source code 2'), common_value)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_value_container(expected, ignore_source_line=False).apply_without_message(put, actual)


class TestEqualsValueDefinition(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            StringConstant('s'),
            FileRefConstant(file_ref_test_impl('file-name')),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    value_container = ValueContainer(Line(1, 'source code'), value)
                    value_definition = ValueDefinition('value name', value_container)
                    # ACT #
                    assertion = sut.equals_value_definition(value_definition, ignore_source_line=ignore_source_line)
                    assertion.apply_without_message(self, value_definition)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value = StringConstant('common string value')
        expected_value_container = ValueContainer(Line(4, 'source code 4'), common_value)
        actual_value_container = ValueContainer(Line(5, 'source code 5'), common_value)
        common_name = 'value name'
        expected_value_definition = ValueDefinition(common_name, expected_value_container)
        actual_value_definition = ValueDefinition(common_name, actual_value_container)
        # ACT #
        assertion = sut.equals_value_definition(expected_value_definition, ignore_source_line=True)
        assertion.apply_without_message(self, actual_value_definition)

    def test_fail__different_name(self):
        # ARRANGE #
        common_value_container = ValueContainer(Line(1, 'source code'),
                                                StringConstant('common string value'))
        expected_value_definition = ValueDefinition('expected value name', common_value_container)
        actual_value_definition = ValueDefinition('actual value name', common_value_container)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_value_definition(expected_value_definition)
            assertion.apply_without_message(put, actual_value_definition)

    def test_fail__failing_assertion_on_value_container(self):
        # ARRANGE #
        common_name_source = Line(1, 'source code')
        common_name = 'value name'
        expected_value_definition = ValueDefinition(common_name,
                                                    ValueContainer(common_name_source,
                                                                   StringConstant('expected string value')))
        actual_value_definition = ValueDefinition(common_name,
                                                  ValueContainer(common_name_source,
                                                                 StringConstant('actual string value')))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_value_definition(expected_value_definition)
            assertion.apply_without_message(put, actual_value_definition)
