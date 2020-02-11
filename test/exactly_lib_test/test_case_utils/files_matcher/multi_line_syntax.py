import unittest

from exactly_lib.definitions import logic
from exactly_lib.test_case_utils.files_matcher.config import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_lines
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import selection_arguments
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import arbitrary_model
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import is_matching_success, \
    is_arbitrary_matching_failure
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseValidMultiLineSyntax)


DIR_TO_CHECK = '.'


class TestParseValidMultiLineSyntax(unittest.TestCase):
    def _check_sub_test(
            self,
            case: SourceCase,
            result_of_main: ValueAssertion[MatchingResult]):
        with self.subTest(case.name):
            integration_check.CHECKER.check(
                self,
                case.source,
                arbitrary_model(),
                arrangement_w_tcds(),
                Expectation(
                    ParseExpectation(
                        source=case.source_assertion,
                    ),
                    ExecutionExpectation(
                        main_result=result_of_main,
                    ),
                ))

    def test_positive(self):
        cases = [
            SourceCase('MATCHER on first line, followed by non-instr line',
                       source=remaining_source_lines([
                           EMPTINESS_CHECK_ARGUMENT,
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_end_of_line(1)
                       ),
            SourceCase('Followed by empty line',
                       source=remaining_source_lines([
                           EMPTINESS_CHECK_ARGUMENT,
                           '',
                       ]),
                       source_assertion=asrt_source.is_at_end_of_line(1)
                       ),
            SourceCase('Selection and matcher on separate lines',
                       source=remaining_source_lines([
                           selection_arguments(name_pattern='*'),
                           EMPTINESS_CHECK_ARGUMENT,
                           '',
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_end_of_line(2)
                       ),
        ]
        for case in cases:
            self._check_sub_test(case,
                                 is_matching_success())

    def test_negative(self):
        cases = [
            SourceCase('Dir on 1st line, Negation and DIR-CONTENTS-MATCHER on 2nd line',
                       source=remaining_source_lines([
                           logic.NOT_OPERATOR_NAME + ' ' + EMPTINESS_CHECK_ARGUMENT,
                       ]),
                       source_assertion=asrt_source.is_at_end_of_line(1)
                       ),
            SourceCase('Dir on 1st line, Negation and DIR-CONTENTS-MATCHER on 2nd line, followed by non-instr lines',
                       source=remaining_source_lines([
                           logic.NOT_OPERATOR_NAME,
                           EMPTINESS_CHECK_ARGUMENT,
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_end_of_line(2)
                       ),
        ]
        for case in cases:
            self._check_sub_test(case,
                                 is_arbitrary_matching_failure())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
