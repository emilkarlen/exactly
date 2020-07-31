import unittest

from exactly_lib.test_case_utils.string_transformer.impl import case_converters as sut
from exactly_lib_test.type_system.logic.string_model.test_resources import string_models


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
        model = string_models.of_lines(input_lines)
        transformer = sut.ToUpperCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        actual_lines = string_models.as_lines_list(actual)

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
        model = string_models.of_lines(input_lines)
        transformer = sut.ToUpperCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        actual_lines = string_models.as_lines_list(actual)

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
        model = string_models.of_lines(input_lines)
        transformer = sut.ToLowerCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        actual_lines = string_models.as_lines_list(actual)

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
        model = string_models.of_lines(input_lines)
        transformer = sut.ToLowerCaseStringTransformer('arbitrary custom')
        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        actual_lines = string_models.as_lines_list(actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)
