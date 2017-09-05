import re
import unittest

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer, \
    SequenceLinesTransformer, CustomLinesTransformer, ReplaceLinesTransformer, SelectLinesTransformer
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import value_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEquals)


class TestEquals(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        custom_transformer_name = 'name of custom transformer'
        cases = [
            (
                IdentityLinesTransformer(),
                IdentityLinesTransformer()
            ),
            (
                CustomLinesTransformer(custom_transformer_name),
                CustomLinesTransformer(custom_transformer_name)
            ),
            (
                ReplaceLinesTransformer(re.compile('regex'), 'replacement'),
                ReplaceLinesTransformer(re.compile('regex'), 'replacement'),
            ),
            (
                SequenceLinesTransformer([]),
                SequenceLinesTransformer([]),
            ),
            (
                SequenceLinesTransformer([IdentityLinesTransformer()]),
                SequenceLinesTransformer([IdentityLinesTransformer()]),
            ),
            (
                SelectLinesTransformer(LineMatcherConstant(True)),
                SelectLinesTransformer(LineMatcherConstant(True)),
            ),
        ]
        for expected, actual in cases:
            with self.subTest(transformer=expected.__class__.__name__):
                # ACT & ASSERT #
                assertion = sut.equals_lines_transformer(expected)
                assertion.apply_without_message(self, actual)

    def test_not_equals__identity(self):
        # ARRANGE #
        expected = IdentityLinesTransformer()

        different_transformers = [
            CustomLinesTransformer('name'),
            SequenceLinesTransformer([]),
            SelectLinesTransformer(LineMatcherConstant(True)),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_lines_transformer(expected)
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

        expected = ReplaceLinesTransformer(expected_regex,
                                           expected_replacement)

        different_transformers = [
            IdentityLinesTransformer(),
            CustomLinesTransformer('custom transformer'),
            SequenceLinesTransformer([]),
            SelectLinesTransformer(LineMatcherConstant(True)),
            ReplaceLinesTransformer(unexpected_regex, expected_replacement),
            ReplaceLinesTransformer(expected_regex, unexpected_replacement),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_lines_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__select(self):
        # ARRANGE #
        expected_line_matcher = LineMatcherConstant(False)
        unexpected_line_matcher = LineMatcherConstant(True)

        expected = SelectLinesTransformer(expected_line_matcher)

        different_transformers = [
            IdentityLinesTransformer(),
            CustomLinesTransformer('custom transformer'),
            SequenceLinesTransformer([]),
            ReplaceLinesTransformer(re.compile('regex pattern'), 'replacement'),
            SelectLinesTransformer(unexpected_line_matcher),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_lines_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__sequence(self):
        # ARRANGE #
        expected = SequenceLinesTransformer([IdentityLinesTransformer()])

        different_transformers = [
            IdentityLinesTransformer(),
            CustomLinesTransformer('custom transformer'),
            SelectLinesTransformer(LineMatcherConstant(False)),
            SequenceLinesTransformer([]),
            SequenceLinesTransformer([CustomLinesTransformer('custom transformer')]),
            SequenceLinesTransformer([SelectLinesTransformer(LineMatcherConstant(False))]),
            SequenceLinesTransformer([IdentityLinesTransformer(),
                                      IdentityLinesTransformer()]),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_lines_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not_equals__custom(self):
        # ARRANGE #
        expected_transformer_name = 'expected name of custom transformer'
        actual_transformer_name = 'actual name of custom transformer'

        # ARRANGE #
        expected = CustomLinesTransformer(expected_transformer_name)

        different_transformers = [
            IdentityLinesTransformer(),
            SequenceLinesTransformer([]),
            CustomLinesTransformer(actual_transformer_name),
            SelectLinesTransformer(LineMatcherConstant(False)),
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_lines_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
