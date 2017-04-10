import unittest

from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib.value_definition.concrete_restrictions import NoRestriction
from exactly_lib.value_definition.concrete_values import StringValue
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import concrete_value_assertions_2 as sut
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_references


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEquals),
        unittest.makeSuite(TestNotEquals),
        unittest.makeSuite(TestNotEquals3),
    ])


class TestEquals(unittest.TestCase):
    def test_with_ignored_reference_checks(self):
        test_cases = [
            ('Plain string',
             'string value',
             StringValue('string value'),
             empty_symbol_table(),
             ),
            ('String with reference',
             'string value',
             _StringValueTestImpl('string value', [ValueReference('symbol_name', NoRestriction())]),
             empty_symbol_table(),
             ),
        ]
        for test_case_name, plain_string, string_value, symbol_table in test_cases:
            assert isinstance(plain_string, str), 'Type info for IDE'
            assert isinstance(string_value, StringValue), 'Type info for IDE'
            with self.subTest(msg='equals_string_value2::' + test_case_name):
                assertion = sut.equals_string_value2(plain_string, asrt.ignore, symbol_table)
                assertion.apply_with_message(self, string_value, test_case_name)
            with self.subTest(msg='equals_string_value2::with checked references::' + test_case_name):
                assertion = sut.equals_string_value2(plain_string, asrt.ignore, symbol_table)
                assertion.apply_with_message(self, string_value, test_case_name)
            with self.subTest(msg='equals_string_value2::with checked references::' + test_case_name):
                assertion = sut.equals_string_value3(string_value)
                assertion.apply_with_message(self, string_value, test_case_name)

    def test_with_used_reference_checks(self):
        test_cases = [
            ('Plain string',
             'string value',
             [],
             empty_symbol_table(),
             ),
            ('String with reference',
             'string value',
             [ValueReference('symbol_name', NoRestriction())],
             empty_symbol_table(),
             ),
        ]
        for test_case_name, plain_string, references, symbol_table in test_cases:
            assert isinstance(plain_string, str), 'Type info for IDE'
            string_value = _StringValueTestImpl(plain_string, references)
            with self.subTest(msg=test_case_name):
                assertion = sut.equals_string_value2(plain_string,
                                                     equals_value_references(references),
                                                     symbol_table)
                assertion.apply_with_message(self, string_value, test_case_name)


class TestNotEquals(unittest.TestCase):
    def test_differs__resolved_value(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        actual = StringValue('actual value')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_value2(expected_string,
                                                 asrt.ignore,
                                                 empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__given_assertion_on_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        actual = StringValue(expected_string)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_value2(expected_string,
                                                 asrt.fail('expected failure'),
                                                 empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__different_number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        actual_references = [ValueReference('actual_symbol_name', NoRestriction())]
        expected_references = [ValueReference('expected_symbol_name', NoRestriction())]
        actual = _StringValueTestImpl(expected_string, actual_references)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_value2(expected_string,
                                                 equals_value_references(expected_references),
                                                 empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')


class TestNotEquals3(unittest.TestCase):
    def test_differs__resolved_value(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected = StringValue(expected_string)
        actual = StringValue('actual value')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_value3(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected = StringValue(expected_string)
        actual = _StringValueTestImpl(expected_string,
                                      [ValueReference('symbol_name', NoRestriction())])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_value3(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_references = [ValueReference('expected_symbol_name', NoRestriction())]
        actual_references = [ValueReference('actual_symbol_name', NoRestriction())]
        expected = _StringValueTestImpl(expected_string, expected_references)
        actual = _StringValueTestImpl(expected_string, actual_references)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_value3(expected)
            assertion.apply_without_message(put, actual)


class _StringValueTestImpl(StringValue):
    def __init__(self,
                 value: str,
                 explicit_references: list):
        super().__init__(value)
        self.explicit_references = explicit_references

    @property
    def references(self) -> list:
        return self.explicit_references
