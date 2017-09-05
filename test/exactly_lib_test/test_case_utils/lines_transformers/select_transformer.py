import unittest

from exactly_lib.test_case_utils.lines_transformer import transformers as sut
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSelect)


class TestSelect(unittest.TestCase):
    def test_select(self):
        home_and_sds = fake_home_and_sds()

        transformer = sut.SelectLinesTransformer(SubStringLineMatcher('MATCH'))
        cases = [
            NameAndValue('no lines',
                         ([],
                          [])
                         ),
            NameAndValue('single line that matches',
                         (['MATCH'],
                          ['MATCH'])
                         ),
            NameAndValue('single line that does not match',
                         (['not a match'],
                          [])
                         ),
            NameAndValue('some lines matches',
                         ([
                              'first line is a MATCH',
                              'second line is not a match',
                              'third line MATCH:es',
                              'fourth line not',
                          ],
                          [
                              'first line is a MATCH',
                              'third line MATCH:es',
                          ])
                         ),
        ]
        for case in cases:
            input_lines, expected_output_lines = case.value
            with self.subTest(case_name=case.name):
                # ACT #
                actual = transformer.transform(home_and_sds, iter(input_lines))
                # ASSERT #
                actual_lines = list(actual)
                self.assertEqual(expected_output_lines,
                                 actual_lines)


class SubStringLineMatcher(LineMatcher):
    def __init__(self, sub_string: str):
        self.sub_string = sub_string

    def matches(self, line: str) -> bool:
        return self.sub_string in line
