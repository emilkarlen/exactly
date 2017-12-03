import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstant)
    ])


class TestConstant(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('constant true should match non-empty line',
                         (
                             True,
                             (1, 'abc abc'),
                             True,
                         )),
            NameAndValue('constant true should match empty line',
                         (
                             True,
                             (2, ''),
                             True,
                         )),
            NameAndValue('constant false should match non-empty line',
                         (
                             False,
                             (3, 'abc abc'),
                             False,
                         )),
            NameAndValue('constant false should match empty line',
                         (
                             False,
                             (3, ''),
                             False,
                         )),
        ]
        for case in cases:
            constant_result, line, expected_result = case.value
            with self.subTest(case_name=case.name):
                matcher = sut.LineMatcherConstant(constant_result)
                # ACT #
                actual_result_constant = matcher.result_constant

                actual_result = matcher.matches(line)

                # ASSERT #

                self.assertEqual(constant_result,
                                 actual_result_constant,
                                 'result constant')

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')
