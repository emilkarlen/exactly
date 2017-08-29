import unittest

from exactly_lib.type_system_values.lines_transformer import CustomLinesTransformer, \
    IdentityLinesTransformer
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_system_values.test_resources import lines_transformer_assertions as sut


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
        ]
        for expected, actual in cases:
            with self.subTest(transformer=expected.__class__.__name__):
                # ACT & ASSERT #
                assertion = sut.equals_lines_transformer(expected)
                assertion.apply_without_message(self, actual)

    def test_not_equals_empty(self):
        # ARRANGE #
        expected_transformer_name = 'expected name of custom transformer'
        actual_transformer_name = 'actual name of custom transformer'

        cases = [
            (
                IdentityLinesTransformer(),
                CustomLinesTransformer('name'),

            ),
            (
                CustomLinesTransformer(expected_transformer_name),
                CustomLinesTransformer(actual_transformer_name),

            ),
        ]
        for expected, actual in cases:
            assertion_to_check = sut.equals_lines_transformer(expected)
            with self.subTest(expected=expected.__class__.__name__,
                              actual=actual.__class__.__name__):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
