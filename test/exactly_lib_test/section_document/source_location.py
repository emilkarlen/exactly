import unittest
from pathlib import Path
from typing import Optional

from exactly_lib.section_document import source_location as sut
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.test_resources.test_utils import NEA


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSourceLocationInfo),
        unittest.makeSuite(TestFileLocationInfo),
    ])


IRRELEVANT_SOURCE = single_line_sequence(1, 'irrelevant source line')


class TestSourceLocationInfo(unittest.TestCase):
    def test_abs_path_of_dir_containing_file(self):
        # ARRANGE #

        abs_path_of_dir_containing_root_file = Path.cwd()

        rel_file_a = Path('rel-file-a')
        rel_file_b = Path('rel-file-b')
        rel_file_c = Path('rel-file-c')
        rel_file_d = Path('rel-file-d')

        cases = [
            NEA('no inclusions',
                expected=abs_path_of_dir_containing_root_file,
                actual=sut.SourceLocationInfo(abs_path_of_dir_containing_root_file,
                                              sut.SourceLocationPath(
                                                  source_location(rel_file_a),
                                                  [],
                                              ))
                ),
            NEA('single inclusion of file in same dir',
                expected=abs_path_of_dir_containing_root_file,
                actual=sut.SourceLocationInfo(abs_path_of_dir_containing_root_file,
                                              sut.SourceLocationPath(
                                                  source_location(rel_file_a),
                                                  [source_location(rel_file_b)],
                                              ))
                ),
            NEA('single inclusion of file in sub dir',
                expected=abs_path_of_dir_containing_root_file / rel_file_b,
                actual=sut.SourceLocationInfo(abs_path_of_dir_containing_root_file,
                                              sut.SourceLocationPath(
                                                  source_location(rel_file_a),
                                                  [source_location(rel_file_b / rel_file_c)],
                                              ))
                ),
            NEA('single inclusion of file in super dir',
                expected=abs_path_of_dir_containing_root_file / Path('..'),
                actual=sut.SourceLocationInfo(abs_path_of_dir_containing_root_file,
                                              sut.SourceLocationPath(
                                                  source_location(rel_file_a),
                                                  [source_location(Path('..') / rel_file_c)],
                                              ))
                ),
            NEA('root link in inclusion chain has no path',
                expected=abs_path_of_dir_containing_root_file,
                actual=sut.SourceLocationInfo(abs_path_of_dir_containing_root_file,
                                              sut.SourceLocationPath(
                                                  source_location(rel_file_a),
                                                  [source_location(rel_file_b),
                                                   source_location(None)],
                                              ))
                ),
            NEA('mix',
                expected=abs_path_of_dir_containing_root_file / Path('..') / rel_file_a,
                actual=sut.SourceLocationInfo(abs_path_of_dir_containing_root_file,
                                              sut.SourceLocationPath(
                                                  source_location(rel_file_a / rel_file_b),
                                                  [source_location(Path('..') / rel_file_c),
                                                   source_location(rel_file_d)],
                                              ))
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual = case.actual.abs_path_of_dir_containing_file

                # ASSERT #

                self.assertEqual(case.expected,
                                 actual)


class TestFileLocationInfo(unittest.TestCase):
    def test_abs_path_of_dir_containing_file(self):
        # ARRANGE #

        abs_path_of_dir_containing_root_file = Path.cwd()

        rel_file_a = Path('rel-file-a')
        rel_file_b = Path('rel-file-b')
        rel_file_c = Path('rel-file-c')
        rel_file_d = Path('rel-file-d')

        cases = [
            NEA('no inclusions',
                expected=abs_path_of_dir_containing_root_file,
                actual=sut.FileLocationInfo(abs_path_of_dir_containing_root_file,
                                            rel_file_a,
                                            [],
                                            )
                ),
            NEA('single inclusion of file in same dir',
                expected=abs_path_of_dir_containing_root_file,
                actual=sut.FileLocationInfo(abs_path_of_dir_containing_root_file,
                                            rel_file_a,
                                            [source_location(rel_file_b)],
                                            )
                ),
            NEA('single inclusion of file in sub dir',
                expected=abs_path_of_dir_containing_root_file / rel_file_b,
                actual=sut.FileLocationInfo(abs_path_of_dir_containing_root_file,
                                            rel_file_a,
                                            [source_location(rel_file_b / rel_file_c)],
                                            )
                ),
            NEA('single inclusion of file in super dir',
                expected=abs_path_of_dir_containing_root_file / Path('..'),
                actual=sut.FileLocationInfo(abs_path_of_dir_containing_root_file,
                                            rel_file_a,
                                            [source_location(Path('..') / rel_file_c)],
                                            )
                ),
            NEA('root link in inclusion chain has no path',
                expected=abs_path_of_dir_containing_root_file,
                actual=sut.FileLocationInfo(abs_path_of_dir_containing_root_file,
                                            rel_file_a,
                                            [source_location(rel_file_b),
                                             source_location(None)
                                             ],
                                            )
                ),
            NEA('mix',
                expected=abs_path_of_dir_containing_root_file / Path('..') / rel_file_a,
                actual=sut.FileLocationInfo(abs_path_of_dir_containing_root_file,
                                            rel_file_a / rel_file_b,
                                            [source_location(Path('..') / rel_file_c),
                                             source_location(rel_file_d)
                                             ],
                                            )
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual = case.actual.abs_path_of_dir_containing_file

                # ASSERT #

                self.assertEqual(case.expected,
                                 actual)


def source_location(file_path_rel_referrer: Optional[Path]) -> sut.SourceLocation:
    return sut.SourceLocation(IRRELEVANT_SOURCE,
                              file_path_rel_referrer)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
