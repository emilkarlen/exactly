import unittest

from exactly_lib.test_case_utils.string_transformer.impl import case_converters as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestToUpper),
        unittest.makeSuite(TestToLower),
    ])


class TestToUpper(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.ToUpperCaseStringTransformer('arbitrary custom')
        self.assertFalse(transformer.is_identity_transformer)

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        input_lines = [
            'I object!',
            'Object Oriented',
            'Unidentified FLYING Object',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ToUpperCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = [
            'I OBJECT!',
            'OBJECT ORIENTED',
            'UNIDENTIFIED FLYING OBJECT',
        ]

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_no_lines(self):
        # ARRANGE #
        input_lines = []
        input_lines_iter = iter(input_lines)
        transformer = sut.ToUpperCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)


class TestToLower(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.ToLowerCaseStringTransformer('arbitrary custom')
        self.assertFalse(transformer.is_identity_transformer)

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        input_lines = [
            'I object!',
            'Object Oriented',
            'Unidentified FLYING Object',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ToLowerCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = [
            'i object!',
            'object oriented',
            'unidentified flying object',
        ]

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_no_lines(self):
        # ARRANGE #
        input_lines = []
        input_lines_iter = iter(input_lines)
        transformer = sut.ToLowerCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)
