import re
import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRegex)
    ])


class TestRegex(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('single character regex that matches',
                         (
                             'a',
                             'abc abc',
                             True,
                         )),
            NameAndValue('single character regex that not matches',
                         (
                             'x',
                             'abc abc',
                             False,
                         )),
            NameAndValue('regex that matches',
                         (
                             'a..d',
                             '__ abcd __',
                             True,
                         )),
            NameAndValue('regex that not matches',
                         (
                             'a..d',
                             '__  __',
                             False,
                         )),
            NameAndValue('dot should not match newline',
                         (
                             '.',
                             '\n',
                             False,
                         )),
        ]
        for case in cases:
            reg_ex_str, line, expected_result = case.value
            with self.subTest(case_name=case.name):
                matcher = sut.LineMatcherRegex(re.compile(reg_ex_str))
                # ACT #
                actual_pattern_str = matcher.regex_pattern_string

                actual_result = matcher.matches((1, line))

                # ASSERT #

                self.assertEqual(reg_ex_str,
                                 actual_pattern_str,
                                 'pattern string')

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')
