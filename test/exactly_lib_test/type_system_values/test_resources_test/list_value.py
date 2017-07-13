import unittest

from exactly_lib.type_system_values import concrete_string_values as csv
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails
from exactly_lib_test.type_system_values.test_resources import list_value as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsStringList),
    ])


class TestEqualsStringList(unittest.TestCase):
    # Few tests here, since the sut has been tested indirectly
    # as it is a slight modification of a generic utility that has been tested elsewhere.

    def test_pass(self):
        cases = [
            (
                'no elements',
                sut.ListValue([]),
            ),
            (
                'single element',
                sut.ListValue([csv.string_value_of_single_string('value')]),
            ),
        ]
        for name, value in cases:
            with self.subTest(name=name):
                assertion = sut.equals_list_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__different_number_of_elements(self):
        # ARRANGE #
        actual = sut.ListValue([])
        expected = sut.ListValue([csv.string_value_of_single_string('value')])

        assertion = sut.equals_list_value(expected)
        # ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_fail__different_fragment_value(self):
        # ARRANGE #
        actual = sut.ListValue([csv.string_value_of_single_string('actual value')])
        expected = sut.ListValue([csv.string_value_of_single_string('expected value')])

        assertion = sut.equals_list_value(expected)
        # ASSERT #
        assert_that_assertion_fails(assertion, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
