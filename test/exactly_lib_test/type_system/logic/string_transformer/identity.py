import unittest

from exactly_lib.test_case_utils.string_transformer.impl import identity as sut
from exactly_lib_test.test_case_utils.test_resources import string_models


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):

    def test_SHOULD_be_identity_transformer(self):
        transformer = sut.IdentityStringTransformer()
        self.assertTrue(transformer.is_identity_transformer)

    def test_empty_list_of_lines(self):
        # ARRANGE #
        input_lines = []
        model = string_models.of_lines(input_lines)
        transformer = sut.IdentityStringTransformer()
        # ACT #

        actual = transformer.transform__new(model)

        # ASSERT #

        actual_lines = string_models.as_lines_list(actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_non_empty_list_of_lines(self):
        # ARRANGE #
        input_lines = [
            'we are here and they are here too',
            'here I am',
            'I am here',
        ]
        model = string_models.of_lines(input_lines)
        transformer = sut.IdentityStringTransformer()
        # ACT #

        actual = transformer.transform__new(model)

        # ASSERT #

        actual_lines = string_models.as_lines_list(actual)

        self.assertEqual(input_lines,
                         actual_lines)
