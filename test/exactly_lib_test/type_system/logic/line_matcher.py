import unittest

from exactly_lib.type_system.logic import line_matcher as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Case:
    def __init__(self,
                 name: str,
                 input_source_lines: iter,
                 expected: list):
        self.name = name
        self.input_source_lines = input_source_lines
        self.expected = expected


class Test(unittest.TestCase):
    def test(self):
        # ARRANGE 3
        cases = [
            Case('empty input should give empty list of models',
                 input_source_lines=[],
                 expected=[]
                 ),

            Case('first line number should be 1',
                 input_source_lines=['a'],
                 expected=[(1, 'a')]
                 ),

            Case('trailing newline should be preserved',
                 input_source_lines=['a\n'],
                 expected=[(1, 'a\n')]
                 ),

            Case('lines should be numbered 1,2,3, ...',
                 input_source_lines=['a\n',
                                     'b\n',
                                     'c\n',
                                     'd'],
                 expected=[(1, 'a\n'),
                           (2, 'b\n'),
                           (3, 'c\n'),
                           (4, 'd'),
                           ]
                 ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = sut.model_iter_from_string_iter(case.input_source_lines)
                # ASSERT #
                actual_list = list(actual)
                self.assertEqual(case.expected,
                                 actual_list)
