import unittest

from exactly_lib.test_case_utils.lines_transformers.transformers import IdentityLinesTransformer, \
    SequenceLinesTransformer, CustomLinesTransformer
from exactly_lib_test.test_case_utils.test_resources import lines_transformer_assertions as sut
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
                SequenceLinesTransformer([]),
                SequenceLinesTransformer([]),
            ),
            (
                SequenceLinesTransformer([IdentityLinesTransformer()]),
                SequenceLinesTransformer([IdentityLinesTransformer()]),
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
            SequenceLinesTransformer([]),
            SequenceLinesTransformer([CustomLinesTransformer('custom transformer')]),
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
        ]
        for actual in different_transformers:
            assertion_to_check = sut.equals_lines_transformer(expected)
            with self.subTest(actual=str(actual)):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
