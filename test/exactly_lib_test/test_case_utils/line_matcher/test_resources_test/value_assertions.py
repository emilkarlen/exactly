import re
import unittest

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant, LineMatcherRegex
from exactly_lib_test.test_case_utils.line_matcher.test_resources import value_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEquals)


class TestEquals(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        cases = [
            (
                LineMatcherConstant(False),
                LineMatcherConstant(False),
            ),
            (
                LineMatcherConstant(True),
                LineMatcherConstant(True),
            ),
            (
                LineMatcherRegex(re.compile('pattern')),
                LineMatcherRegex(re.compile('pattern')),
            ),
        ]
        for expected, actual in cases:
            with self.subTest(transformer=expected.__class__.__name__):
                # ACT & ASSERT #
                assertion = sut.equals_line_matcher(expected)
                assertion.apply_without_message(self, actual)

    def test_not_equals__constant(self):
        # ARRANGE #
        for constant_result in [False, True]:
            expected = LineMatcherConstant(constant_result)

            different_transformers = [
                LineMatcherConstant(not constant_result),
                LineMatcherRegex(re.compile('pattern')),
            ]
            for actual in different_transformers:
                assertion_to_check = sut.equals_line_matcher(expected)
                with self.subTest(constant_result=constant_result,
                                  actual=str(actual)):
                    # ACT & ASSERT #
                    assert_that_assertion_fails(assertion_to_check,
                                                actual)

    def test_not_equals__regex(self):
        # ARRANGE #
        expected_regex = re.compile('expected_regex')

        unexpected_regex = re.compile('unexpected_regex')

        expected = LineMatcherRegex(expected_regex)

        different_transformers = [
            LineMatcherConstant(False),
            LineMatcherConstant(True),
            LineMatcherRegex(unexpected_regex)
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_line_matcher(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
