import unittest

from exactly_lib.util import file_printables
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import file_printable_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatches),
        unittest.makeSuite(TestEqualsString),
        unittest.makeSuite(TestEquals),
    ])


class TestMatches(unittest.TestCase):
    def test_default_assertion_SHOULD_match_anything(self):
        # ARRANGE #
        assertion = sut.matches()
        cases = [
            '',
            'some text',
        ]
        for case in cases:
            with self.subTest(case):
                actual = file_printables.of_constant_string(case)
                # ACT & ASSERT #
                assertion.apply_without_message(self, actual)

    def test_fail_WHEN_actual_is_and_object_of_invalid_type(self):
        # ARRANGE #
        assertion = sut.matches(asrt.anything_goes())
        actual = 'not a file printable'

        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_matches_explicit_assertion(self):
        # ARRANGE #
        expected_str = 'the text'
        assertion = sut.matches(asrt.equals(expected_str))
        actual = file_printables.of_constant_string(expected_str)

        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches_explicit_assertion(self):
        # ARRANGE #
        assertion = sut.matches(asrt.equals('expected'))
        actual = file_printables.of_constant_string('actual')

        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class TestEqualsString(unittest.TestCase):
    def test_equals_str(self):
        # ARRANGE #
        expected_str = 'the text'
        assertion = sut.equals_string(expected_str)
        actual = file_printables.of_constant_string(expected_str)

        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_str(self):
        # ARRANGE #
        assertion = sut.equals_string('expected')
        actual = file_printables.of_constant_string('actual')

        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class TestEquals(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        expected_str = 'the text'
        expected = file_printables.of_constant_string(expected_str)
        actual = file_printables.of_constant_string(expected_str)

        assertion = sut.equals(expected)

        # ACT & ASSERT #

        assertion.apply_without_message(self, actual)

    def test_not_equals(self):
        # ARRANGE #
        expected = file_printables.of_constant_string('expected')
        actual = file_printables.of_constant_string('actual')

        assertion = sut.equals(expected)

        # ACT & ASSERT #

        assert_that_assertion_fails(assertion, actual)
