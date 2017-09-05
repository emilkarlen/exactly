import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib_test.test_case_utils.line_matcher.test_resources import value_assertions as asrt_lm
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def _check(self, case_name: str,
               anded_matchers: list,
               expected_result: bool):
        matcher = sut.LineMatcherAnd(anded_matchers)
        with self.subTest(sub_case_name=case_name):
            # ACT #
            actual_matchers = matcher.matchers

            actual_result = matcher.matches('line with irrelevant content')

            # ASSERT #

            self.assertEqual(expected_result,
                             actual_result,
                             'result')

            assertion_on_matchers = asrt.matches_sequence(list(map(asrt_lm.equals_line_matcher, anded_matchers)))
            assertion_on_matchers.apply_with_message(self, actual_matchers,
                                                     'matchers')

    def test_empty_list_of_matchers_SHOULD_evaluate_to_tro(self):
        self._check('',
                    [],
                    True)

    def test_single_matcher_SHOULD_evaluate_to_value_of_the_single_matcher(self):
        cases = [
            NameAndValue('false',
                         (
                             [LineMatcherConstant(False)],
                             False,
                         )),
            NameAndValue('true',
                         (
                             [LineMatcherConstant(True)],
                             True,
                         )),
        ]
        for case in cases:
            anded_matchers, expected_result = case.value
            self._check(case.name,
                        anded_matchers,
                        expected_result)

    def test_more_than_one_matcher_SHOULD_evaluate_to_True_WHEN_all_matchers_evaluate_to_True(self):
        cases = [
            NameAndValue('two matchers',
                         [LineMatcherConstant(True),
                          LineMatcherConstant(True)],
                         ),
            NameAndValue('three matchers',
                         [LineMatcherConstant(True),
                          LineMatcherConstant(True),
                          LineMatcherConstant(True)],
                         ),
        ]
        for case in cases:
            anded_matchers = case.value
            self._check(case.name,
                        anded_matchers,
                        True)

    def test_more_than_one_matcher_SHOULD_evaluate_to_False_WHEN_any_matcher_evaluates_to_False(self):
        cases = [
            NameAndValue('two matchers/first is false',
                         [LineMatcherConstant(False),
                          LineMatcherConstant(True)],
                         ),
            NameAndValue('two matchers/second is false',
                         [LineMatcherConstant(True),
                          LineMatcherConstant(False)],
                         ),
            NameAndValue('three matchers',
                         [LineMatcherConstant(True),
                          LineMatcherConstant(False),
                          LineMatcherConstant(True)],
                         ),
        ]
        for case in cases:
            self._check(case.name,
                        case.value,
                        False)
