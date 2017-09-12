import re
import unittest

from exactly_lib.test_case_utils.lines_transformer import transformers as sut
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    tcds = fake_home_and_sds()

    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.ReplaceLinesTransformer(re.compile('object'),
                                                  'transformer')
        self.assertFalse(transformer.is_identity_transformer)

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        input_lines = [
            'unidentified flying object',
            'object oriented',
            'I object!',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ReplaceLinesTransformer(re.compile('object'),
                                                  'transformer')
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = [
            'unidentified flying transformer',
            'transformer oriented',
            'I transformer!',
        ]

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_every_match_on_a_line_SHOULD_be_replaced(self):
        # ARRANGE #
        input_lines = [
            'we are here and they are here too',
            'here I am',
            'I am here',
        ]
        expected_lines = [
            'we are there and they are there too',
            'there I am',
            'I am there',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ReplaceLinesTransformer(re.compile('here'),
                                                  'there')
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_regular_expression_SHOULD_be_matched(self):
        # ARRANGE #
        lines = [
            'Exactly',
        ]
        expected_lines = [
            'is what I want',
        ]
        input_lines_iter = iter(lines)
        transformer = sut.ReplaceLinesTransformer(re.compile('[E][x][a][c][t][l][y]'),
                                                  'is what I want')
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_newline_ends_SHOULD_be_included_in_the_transformation(self):
        # ARRANGE #
        lines = [
            '\n',
            '',
        ]
        expected_lines = [
            '',
            '',
        ]
        input_lines_iter = iter(lines)
        transformer = sut.ReplaceLinesTransformer(re.compile('\n'),
                                                  '')
        # ACT #

        actual = transformer.transform(self.tcds, input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(expected_lines,
                         actual_lines)
