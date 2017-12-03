import unittest

from exactly_lib.test_case_utils.lines_transformer import case_converters as sut
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestToUpper),
        unittest.makeSuite(TestToLower),
    ])


class TestToUpper(unittest.TestCase):
    tcds = fake_home_and_sds()

    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.ToUpperCaseLinesTransformer()
        self.assertFalse(transformer.is_identity_transformer)

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        input_lines = [
            'I object!',
            'Object Oriented',
            'Unidentified FLYING Object',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ToUpperCaseLinesTransformer()
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

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
        transformer = sut.ToUpperCaseLinesTransformer()
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)


class TestToLower(unittest.TestCase):
    tcds = fake_home_and_sds()

    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.ToLowerCaseLinesTransformer()
        self.assertFalse(transformer.is_identity_transformer)

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        input_lines = [
            'I object!',
            'Object Oriented',
            'Unidentified FLYING Object',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ToLowerCaseLinesTransformer()
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

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
        transformer = sut.ToLowerCaseLinesTransformer()
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)
