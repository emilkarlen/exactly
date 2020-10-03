from abc import ABC

from exactly_lib_test.test_case_utils.file_matcher.names.test_resources import configuration
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources.checkers import check_glob
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources.configuration import Case
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check


class TestGlobPattern(configuration.TestCaseBase, ABC):
    def runTest(self):
        cases = [
            Case(
                'full tail',
                True,
                model_tail='abc',
                pattern='*abc',
            ),
            Case(
                'full tail',
                False,
                model_tail='xyz',
                pattern='*abc',
            ),
            Case(
                'substring',
                True,
                model_tail='abc',
                pattern='*b*',
            ),
            Case(
                'substring',
                False,
                model_tail='axc',
                pattern='*b*',
            ),
            Case(
                'any character',
                True,
                model_tail='ab',
                pattern='*?b',
            ),
            Case(
                'any character',
                False,
                model_tail='abc',
                pattern='*?b',
            ),
            Case(
                'character group',
                True,
                model_tail='ae',
                pattern='*[abc][def]',
            ),
            Case(
                'character group',
                False,
                model_tail='x',
                pattern='*[abc]',
            ),
            Case(
                'negated character group',
                True,
                model_tail='xe',
                pattern='*[!abc][def]',
            ),
            Case(
                'negated character group',
                False,
                model_tail='a',
                pattern='*[!abc]',
            ),
            Case(
                'character range',
                True,
                model_tail='ax',
                pattern='*[a-c][x-y]',
            ),
            Case(
                'character range',
                False,
                model_tail='ab',
                pattern='*[a-c][x-y]',
            ),
            Case(
                'quoted pattern char',
                True,
                model_tail='a?',
                pattern='*a[?]',
            ),
        ]
        for case in cases:
            with self.subTest(case.name,
                              expected_result=case.expected_result):
                check_glob(
                    self,
                    self.conf,
                    case.pattern,
                    integration_check.constant_relative_file_name(
                        self.conf.file_name_ending_with(case.model_tail)
                    ),
                    case.expected_result,
                )
