import pathlib
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestGlobPattern)


class TestGlobPattern(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('match basename with exact match',
                         (
                             'pattern',
                             pathlib.Path('pattern'),
                             True,
                         )),
            NameAndValue('match basename with substring exact match',
                         (
                             '*PATTERN*',
                             pathlib.Path('before PATTERN after'),
                             True,
                         )),
            NameAndValue('match basename with substring exact match',
                         (
                             '*PATTERN*',
                             pathlib.Path('before PATTERN after'),
                             True,
                         )),
            NameAndValue('match name with pattern that matches path components',
                         (
                             'dir-name/*.txt',
                             pathlib.Path('dir-name') / pathlib.Path('file.txt'),
                             True,
                         )),
            NameAndValue('not match, because pattern is not in path',
                         (
                             'PATTERN',
                             pathlib.Path('not the pattern'),
                             False,
                         )),
        ]
        for case in cases:
            glob_pattern, path, expected_result = case.value
            with self.subTest(case_name=case.name,
                              glob_pattern=glob_pattern):
                matcher = sut.FileMatcherNameGlobPattern(glob_pattern)
                # ACT #
                actual_glob_pattern = matcher.glob_pattern

                actual_result = matcher.matches(path)

                # ASSERT #

                self.assertIsInstance(matcher.option_description,
                                      str,
                                      'option_description')

                self.assertEqual(glob_pattern,
                                 actual_glob_pattern,
                                 'result constant')

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')
