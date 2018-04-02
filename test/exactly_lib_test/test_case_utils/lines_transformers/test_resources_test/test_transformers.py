import unittest

from exactly_lib_test.test_case_utils.lines_transformers.test_resources import resolver_assertions as sut
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import test_transformers as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDuplicateWordsTransformer),
        unittest.makeSuite(TestDeleteInitialWordTransformer),
    ])


class TestDuplicateWordsTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.DuplicateWordsTransformer()
        self.assertFalse(transformer.is_identity_transformer)

    def test_no_lines(self):
        # ARRANGE #

        transformer = sut.DuplicateWordsTransformer()

        # ACT #

        actual = transformer.transform([])

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual([], actual_as_list)

    def test_empty_lines(self):
        # ARRANGE #

        transformer = sut.DuplicateWordsTransformer()
        input_lines = [
            '\n',
            '  \n',
            '  ',
            ''
        ]
        expected = [
            '\n',
            '\n',
            '',
            '',
        ]

        # ACT #

        actual = transformer.transform(input_lines)

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual(expected, actual_as_list)

    def test_lines_with_words(self):
        # ARRANGE #

        transformer = sut.DuplicateWordsTransformer()
        input_lines = [' a\n',
                       ' first second \n',
                       '%']

        # ACT #

        actual = transformer.transform(input_lines)

        # ASSERT #

        actual_as_list = list(actual)
        expected = ['a a\n',
                    'first first second second\n',
                    '% %']

        self.assertEqual(expected, actual_as_list)


class TestDeleteInitialWordTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.DeleteInitialWordTransformer()
        self.assertFalse(transformer.is_identity_transformer)

    def test_no_lines(self):
        # ARRANGE #

        transformer = sut.DeleteInitialWordTransformer()

        # ACT #

        actual = transformer.transform([])

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual([], actual_as_list)

    def test_empty_lines(self):
        # ARRANGE #

        transformer = sut.DeleteInitialWordTransformer()
        input_lines = ['\n',
                       '  \n',
                       '  ',
                       '']
        expected = ['\n',
                    '\n',
                    '',
                    '']

        # ACT #

        actual = transformer.transform(input_lines)

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual(expected, actual_as_list)

    def test_lines_with_words(self):
        # ARRANGE #

        transformer = sut.DeleteInitialWordTransformer()
        input_lines = [' a\n',
                       ' first second \n',
                       '%']

        # ACT #

        actual = transformer.transform(input_lines)

        # ASSERT #

        actual_as_list = list(actual)
        expected = ['\n',
                    'second\n',
                    '']

        self.assertEqual(expected, actual_as_list)
