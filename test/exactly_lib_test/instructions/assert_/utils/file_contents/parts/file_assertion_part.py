import unittest

from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib_test.instructions.assert_.utils.file_contents.test_resources import \
    destination_file_path_getter_that_gives_seq_of_unique_paths
from exactly_lib_test.test_case_utils.string_matcher.test_resources.contents_transformation import \
    ToUppercaseStringTransformer
from exactly_lib_test.test_resources.files.file_utils import tmp_file_containing
from exactly_lib_test.type_system.data.test_resources import described_path


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Case:
    def __init__(self,
                 name: str,
                 file_contents: str,
                 expected: list):
        self.name = name
        self.file_contents = file_contents
        self.expected = expected


class Test(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            Case('empty input should give empty list of models',
                 file_contents='',
                 expected=[]
                 ),

            Case('single line without trailing newline',
                 file_contents='a',
                 expected=['a']
                 ),

            Case('single line with trailing newline',
                 file_contents='a\n',
                 expected=['a\n']
                 ),

            Case('multiple lines',
                 file_contents='a\nb\n',
                 expected=['a\n',
                           'b\n',
                           ]
                 ),
        ]

        line_trans_cases = [
            ('identity', IdentityStringTransformer(), lambda x: x),
            ('to-upper', ToUppercaseStringTransformer(), str.upper),
        ]

        with destination_file_path_getter_that_gives_seq_of_unique_paths() as dst_file_path_getter:
            # This test is expected to not create files using the above object,
            # but to be sure, one is used that creates and destroys temporary files.
            for case in cases:
                with tmp_file_containing(case.file_contents) as actual_file_path:
                    for trans_name, lines_trans, corresponding_expected_trans in line_trans_cases:
                        with self.subTest(case=case.name,
                                          trans=trans_name):
                            ftc = FileToCheck(described_path.new_primitive(actual_file_path),
                                              lines_trans,
                                              dst_file_path_getter)
                            # ACT #
                            with ftc.lines() as lines:
                                # ASSERT #
                                actual_list = list(lines)
                                expected_adapted_to_transformer = list(map(corresponding_expected_trans, case.expected))
                                self.assertEqual(expected_adapted_to_transformer,
                                                 actual_list)
