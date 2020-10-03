from abc import ABC
from typing import Sequence

from exactly_lib_test.test_case_utils.file_matcher.names.test_resources import configuration
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources.checkers import check_regex
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources.configuration import Case
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check


class TestRegEx(configuration.TestCaseBase, ABC):
    def test_case_matters(self):
        # ARRANGE #
        cases = [
            Case(
                'case matters',
                False,
                model_tail='a',
                pattern='A',
            ),
            Case(
                'plain characters',
                True,
                model_tail='abc',
                pattern='abc',
            ),
            Case(
                'plain characters',
                False,
                model_tail='abc',
                pattern='abx',
            ),

            Case(
                'substring',
                True,
                model_tail='abc',
                pattern='b',
            ),
            Case(
                'substring',
                False,
                model_tail='abc',
                pattern='x',
            ),
            Case(
                'any character',
                True,
                model_tail='abc',
                pattern='a.c',
            ),
            Case(
                'zero or more',
                True,
                model_tail='abb',
                pattern='x*a*b*',
            ),
            Case(
                'one or more',
                True,
                model_tail='abb',
                pattern='a+b+',
            ),
            Case(
                'string end',
                True,
                model_tail='abc',
                pattern='abc$',
            ),
            Case(
                'string end',
                False,
                model_tail='abc',
                pattern='ab$',
            ),
            Case(
                'any character',
                True,
                model_tail='ab',
                pattern='a.',
            ),
            Case(
                'any character',
                False,
                model_tail='ab',
                pattern='x.',
            ),
            Case(
                'repetition',
                True,
                model_tail='abc',
                pattern='[abc]{3}',
            ),
            Case(
                'repetition',
                False,
                model_tail='abc',
                pattern='[abc]{4}',
            ),
            Case(
                'choice',
                True,
                model_tail='abc',
                pattern='(abc|def)',
            ),
            Case(
                'choice',
                False,
                model_tail='abc',
                pattern='(def|xyz)',
            ),

            Case(
                'character group',
                True,
                model_tail='ae',
                pattern='[abc][def]',
            ),
            Case(
                'character group',
                False,
                model_tail='x',
                pattern='[abc]',
            ),
            Case(
                'negated character group',
                True,
                model_tail='xe',
                pattern='[^abc][def]',
            ),
            Case(
                'negated character group',
                False,
                model_tail='a',
                pattern='[^abc]$',
            ),
            Case(
                'character range',
                True,
                model_tail='ax',
                pattern='[a-c][x-y]',
            ),
            Case(
                'character range',
                False,
                model_tail='ab',
                pattern='[a-c][x-y]',
            ),
        ]
        # ACT & ASSERT #
        self._check_cases(cases, ignore_case=False)

    def test_ignore_case(self):
        cases = [
            Case(
                'case do not matter',
                True,
                model_tail='a',
                pattern='A',
            ),
        ]
        # ACT & ASSERT #
        self._check_cases(cases, ignore_case=True)

    def _check_cases(self,
                     cases: Sequence[Case],
                     ignore_case: bool):
        for case in cases:
            with self.subTest(case.name,
                              expected_result=case.expected_result):
                check_regex(
                    self,
                    self.conf,
                    case.pattern,
                    ignore_case,
                    integration_check.constant_relative_file_name(
                        self.conf.file_name_ending_with(case.model_tail)
                    ),
                    case.expected_result,
                )
