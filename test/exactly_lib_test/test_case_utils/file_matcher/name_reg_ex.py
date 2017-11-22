import pathlib
import re
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestRegExPatternOnBaseName)


class TestRegExPatternOnBaseName(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('match basename with exact match',
                         (
                             '.*name',
                             pathlib.Path('file name'),
                             True,
                         )),
            NameAndValue('match basename with substring match',
                         (
                             'PA..ERN',
                             pathlib.Path('before PATTERN after'),
                             True,
                         )),
            NameAndValue('match name with pattern that matches path components',
                         (
                             'dir-name',
                             pathlib.Path('dir-name') / pathlib.Path('base-name'),
                             False,
                         )),
            NameAndValue('not match, because pattern is not in path',
                         (
                             'PATTERN',
                             pathlib.Path('not the pattern'),
                             False,
                         )),
        ]
        for case in cases:
            reg_ex_pattern, path, expected_result = case.value
            with self.subTest(case_name=case.name,
                              glob_pattern=reg_ex_pattern):
                matcher = sut.FileMatcherBaseNameRegExPattern(re.compile(reg_ex_pattern))
                # ACT #
                actual_reg_ex_pattern = matcher.reg_ex_pattern

                actual_result = matcher.matches(path)

                # ASSERT #

                self.assertIsInstance(matcher.option_description,
                                      str,
                                      'option_description')

                self.assertEqual(reg_ex_pattern,
                                 actual_reg_ex_pattern,
                                 'reg-ex pattern')

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')
