import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib_test.test_case_utils.line_matcher.test_resources import value_assertions as asrt_lm
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test)
    ])


class Test(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('negate to make negated matcher match',
                         (
                             LineMatcherConstant(False),
                             'line with irrelevant content',
                             True,
                         )),
            NameAndValue('negate to make negated matcher not match',
                         (
                             LineMatcherConstant(True),
                             'line with irrelevant content',
                             False,
                         )),
        ]
        for case in cases:
            negated_matcher, line, expected_result = case.value
            with self.subTest(case_name=case.name):
                matcher = sut.LineMatcherNot(negated_matcher)
                # ACT #
                actual_negated_matcher = matcher.negated_matcher

                actual_result = matcher.matches(line)

                # ASSERT #

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')

                assertion_on_negated_matcher = asrt_lm.equals_line_matcher(negated_matcher)
                assertion_on_negated_matcher.apply_with_message(self, actual_negated_matcher,
                                                                'negated matcher')
