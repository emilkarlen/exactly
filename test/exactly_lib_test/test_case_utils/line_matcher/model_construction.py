import unittest
from typing import List

from exactly_lib.test_case_utils.line_matcher import model_construction as sut
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Case:
    def __init__(self,
                 name: str,
                 input_source_lines: List[str],
                 expected: List[LineMatcherLine],
                 ):
        self.name = name
        self.input_source_lines = input_source_lines
        self.expected = expected


class Test(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            Case('empty input should give empty list of models',
                 input_source_lines=[],
                 expected=[]
                 ),

            Case('first line number should be 1',
                 input_source_lines=['a'],
                 expected=[(1, 'a')]
                 ),

            Case('trailing newline should be removed',
                 input_source_lines=['a\n'],
                 expected=[(1, 'a')]
                 ),

            Case('trailing newline should be removed, but not space before it',
                 input_source_lines=['a \n'],
                 expected=[(1, 'a ')]
                 ),

            Case('trailing non-newline space should be removed',
                 input_source_lines=['a  '],
                 expected=[(1, 'a  ')]
                 ),

            Case('space at start of line should be preserved',
                 input_source_lines=[' a'],
                 expected=[(1, ' a')]
                 ),

            Case('lines should be numbered 1,2,3, ...',
                 input_source_lines=['a\n',
                                     'b\n',
                                     'c\n',
                                     'd'],
                 expected=[(1, 'a'),
                           (2, 'b'),
                           (3, 'c'),
                           (4, 'd'),
                           ]
                 ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = sut.model_iter_from_file_line_iter(case.input_source_lines)
                # ASSERT #
                actual_list = list(actual)
                self.assertEqual(case.expected,
                                 actual_list)
