import unittest
from typing import List, Sequence

from exactly_lib.util.str_ import read_lines as sut
from exactly_lib_test.test_resources.test_utils import ArrEx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestReadLines(),
    ])


class TestReadLines(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in cases():
            for read_case in case.expectation:
                with self.subTest(
                        input_=case.arrangement,
                        min_num_chars_to_read=read_case.min_num_chars_to_read,
                        string=read_case.string,
                        may_have_more_contents=read_case.may_have_more_contents,
                ):
                    # ACT #
                    contents, may_have_more = sut.read_lines_as_str__w_minimum_num_chars(
                        read_case.min_num_chars_to_read,
                        case.arrangement
                    )
                    # ASSERT #
                    self.assertEqual(read_case.string, contents,
                                     'string read')
                    self.assertEqual(read_case.may_have_more_contents, may_have_more,
                                     'may have more contents')


class ReadCase:
    def __init__(self,
                 min_num_chars_to_read: int,
                 string: str,
                 may_have_more_contents: bool,
                 ):
        self.min_num_chars_to_read = min_num_chars_to_read
        self.string = string
        self.may_have_more_contents = may_have_more_contents


def cases() -> Sequence[ArrEx[List[str], List[ReadCase]]]:
    return [
        ArrEx(
            [],
            [
                ReadCase(
                    1,
                    '',
                    False,
                )
            ],
        ),
        ArrEx(
            ['12'],
            [
                ReadCase(
                    1,
                    '12',
                    True,
                ),
                ReadCase(
                    2,
                    '12',
                    True,
                ),
                ReadCase(
                    3,
                    '12',
                    False,
                ),
            ],
        ),
        ArrEx(
            ['12\n'],
            [
                ReadCase(
                    1,
                    '12\n',
                    True,
                ),
                ReadCase(
                    3,
                    '12\n',
                    True,
                ),
                ReadCase(
                    4,
                    '12\n',
                    False,
                ),
            ],
        ),
        ArrEx(
            ['12\n', 'ab'],
            [
                ReadCase(
                    1,
                    '12\n',
                    True,
                ),
                ReadCase(
                    3,
                    '12\n',
                    True,
                ),
                ReadCase(
                    4,
                    '12\nab',
                    True,
                ),
                ReadCase(
                    5,
                    '12\nab',
                    True,
                ),
                ReadCase(
                    6,
                    '12\nab',
                    False,
                ),
            ],
        ),
        ArrEx(
            ['12\n', 'a\n', 'ijk'],
            [
                ReadCase(
                    1,
                    '12\n',
                    True,
                ),
                ReadCase(
                    3,
                    '12\n',
                    True,
                ),
                ReadCase(
                    4,
                    '12\na\n',
                    True,
                ),
                ReadCase(
                    5,
                    '12\na\n',
                    True,
                ),
                ReadCase(
                    6,
                    '12\na\nijk',
                    True,
                ),
                ReadCase(
                    8,
                    '12\na\nijk',
                    True,
                ),
                ReadCase(
                    9,
                    '12\na\nijk',
                    False,
                ),
                ReadCase(
                    10,
                    '12\na\nijk',
                    False,
                ),
            ],
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
