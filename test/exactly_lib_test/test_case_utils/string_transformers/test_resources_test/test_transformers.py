import unittest

from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDeleteEverythingTransformer),
        unittest.makeSuite(TestDuplicateWordsTransformer),
        unittest.makeSuite(TestDeleteInitialWordTransformer),
    ])


class TestDeleteEverythingTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = string_transformers.delete_everything()
        self.assertFalse(transformer.is_identity_transformer)

    def test_no_lines(self):
        # ARRANGE #

        transformer = string_transformers.delete_everything()

        # ACT #

        actual = transformer.transform([])

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual([], actual_as_list)

    def test_lines_SHOULD_be_removed(self):
        # ARRANGE #

        transformer = string_transformers.delete_everything()
        input_lines = [
            'something\n',
            ''
        ]
        # ACT #

        actual = transformer.transform(input_lines)

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual([], actual_as_list)


class TestDuplicateWordsTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = string_transformers.duplicate_words()
        self.assertFalse(transformer.is_identity_transformer)

    def test_no_lines(self):
        # ARRANGE #

        transformer = string_transformers.duplicate_words()

        # ACT #

        actual = transformer.transform([])

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual([], actual_as_list)

    def test_empty_lines(self):
        # ARRANGE #

        transformer = string_transformers.duplicate_words()
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

        transformer = string_transformers.duplicate_words()
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
        transformer = string_transformers.delete_initial_word()
        self.assertFalse(transformer.is_identity_transformer)

    def test_no_lines(self):
        # ARRANGE #

        transformer = string_transformers.delete_initial_word()

        # ACT #

        actual = transformer.transform([])

        # ASSERT #

        actual_as_list = list(actual)
        self.assertEqual([], actual_as_list)

    def test_empty_lines(self):
        # ARRANGE #

        transformer = string_transformers.delete_initial_word()
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

        transformer = string_transformers.delete_initial_word()
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
