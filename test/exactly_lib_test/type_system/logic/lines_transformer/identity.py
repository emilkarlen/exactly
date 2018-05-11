import unittest

from exactly_lib.type_system.logic import string_transformer as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):

    def test_SHOULD_be_identity_transformer(self):
        transformer = sut.IdentityStringTransformer()
        self.assertTrue(transformer.is_identity_transformer)

    def test_empty_list_of_lines(self):
        # ARRANGE #
        input_lines = []
        input_lines_iter = iter(input_lines)
        transformer = sut.IdentityStringTransformer()
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

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
        input_lines_iter = iter(input_lines)
        transformer = sut.IdentityStringTransformer()
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(input_lines,
                         actual_lines)
