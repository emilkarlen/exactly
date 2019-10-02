import re
import unittest

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.string_transformer.impl.replace import ReplaceStringTransformer
from exactly_lib.test_case_utils.string_transformer.impl.select import SelectStringTransformer
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer, SequenceStringTransformer, \
    CustomStringTransformer
from exactly_lib_test.test_case_utils.string_transformers.test_resources import value_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEquals)


class TestEquals(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        cases = [
            (
                IdentityStringTransformer(),
                IdentityStringTransformer()
            ),
            (
                CustomStringTransformer('arbitrary custom'),
                CustomStringTransformer('arbitrary custom')
            ),
            (
                ReplaceStringTransformer(re.compile('regex'), 'replacement'),
                ReplaceStringTransformer(re.compile('regex'), 'replacement'),
            ),
            (
                SequenceStringTransformer([]),
                SequenceStringTransformer([]),
            ),
            (
                SequenceStringTransformer([IdentityStringTransformer()]),
                SequenceStringTransformer([IdentityStringTransformer()]),
            ),
            (
                SelectStringTransformer(LineMatcherConstant(True)),
                SelectStringTransformer(LineMatcherConstant(True)),
            ),
        ]
        for expected, actual in cases:
            with self.subTest(transformer=expected.__class__.__name__):
                # ACT & ASSERT #
                assertion = sut.equals_string_transformer(expected)
                assertion.apply_without_message(self, actual)

    def test_not_equals__identity(self):
        # ARRANGE #
        expected = IdentityStringTransformer()

        different_transformers = [
            CustomStringTransformer('custom transformer'),
            SequenceStringTransformer([]),
            SelectStringTransformer(LineMatcherConstant(True)),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_string_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__replace(self):
        # ARRANGE #
        expected_regex = re.compile('expected_regex')
        expected_replacement = 'expected_replacement'

        unexpected_regex = re.compile('unexpected_regex')
        unexpected_replacement = 'unexpected_replacement'

        expected = ReplaceStringTransformer(expected_regex,
                                            expected_replacement)

        different_transformers = [
            IdentityStringTransformer(),
            CustomStringTransformer('arbitrary custom'),
            SequenceStringTransformer([]),
            SelectStringTransformer(LineMatcherConstant(True)),
            ReplaceStringTransformer(unexpected_regex, expected_replacement),
            ReplaceStringTransformer(expected_regex, unexpected_replacement),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_string_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__select(self):
        # ARRANGE #
        expected_line_matcher = LineMatcherConstant(False)
        unexpected_line_matcher = LineMatcherConstant(True)

        expected = SelectStringTransformer(expected_line_matcher)

        different_transformers = [
            IdentityStringTransformer(),
            CustomStringTransformer('arbitrary custom'),
            SequenceStringTransformer([]),
            ReplaceStringTransformer(re.compile('regex pattern'), 'replacement'),
            SelectStringTransformer(unexpected_line_matcher),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_string_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__sequence(self):
        # ARRANGE #
        expected = SequenceStringTransformer([IdentityStringTransformer()])

        different_transformers = [
            IdentityStringTransformer(),
            CustomStringTransformer('arbitrary custom'),
            SelectStringTransformer(LineMatcherConstant(False)),
            SequenceStringTransformer([]),
            SequenceStringTransformer([CustomStringTransformer('arbitrary custom')]),
            SequenceStringTransformer([SelectStringTransformer(LineMatcherConstant(False))]),
            SequenceStringTransformer([IdentityStringTransformer(),
                                       IdentityStringTransformer()]),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_string_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__custom(self):
        # ARRANGE #
        expected = CustomStringTransformer('arbitrary custom')

        different_transformers = [
            IdentityStringTransformer(),
            SequenceStringTransformer([]),
            SelectStringTransformer(LineMatcherConstant(False)),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_string_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
