import unittest

from exactly_lib.definitions import instruction_arguments
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.contents_of_dir.config import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.test_case.result.pfh import PassOrFailOrHardErrorEnum
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_lines
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_syntax import selection_arguments
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseValidMultiLineSyntax)


DIR_TO_CHECK = '.'


class TestParseValidMultiLineSyntax(unittest.TestCase):
    def _check_sub_test(
            self,
            case: SourceCase,
            result_of_main: PassOrFailOrHardErrorEnum):
        with self.subTest(case.name):
            instruction_check.check(
                self,
                sut.setup('instruction-name'),
                case.source,
                ArrangementPostAct(),
                Expectation(
                    main_result=pfh_assertions.status_is(result_of_main),
                    source=case.source_assertion,
                ))

    def test_positive(self):
        cases = [
            SourceCase('Dir on first line, DIR-CONTENTS-MATCHER on following line',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           EMPTINESS_CHECK_ARGUMENT,
                       ]),
                       source_assertion=asrt_source.source_is_at_end
                       ),
            SourceCase('Dir on first line, DIR-CONTENTS-MATCHER on following line, followed by non-instr line',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           EMPTINESS_CHECK_ARGUMENT,
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_beginning_of_line(3)
                       ),
            SourceCase('Empty lines between arguments',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           '',
                           EMPTINESS_CHECK_ARGUMENT,
                           '',
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_beginning_of_line(4)
                       ),
            SourceCase('Followed by empty line '
                       '(a bit strange behaviour - should probably be at beginning of last line)',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           EMPTINESS_CHECK_ARGUMENT,
                           '',
                       ]),
                       source_assertion=asrt_source.source_is_at_end
                       ),
            SourceCase('With selection on separate line',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           selection_arguments(name_pattern='*'),
                           EMPTINESS_CHECK_ARGUMENT,
                           '',
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_beginning_of_line(4)
                       ),
        ]
        for case in cases:
            self._check_sub_test(case,
                                 PassOrFailOrHardErrorEnum.PASS)

    def test_negative(self):
        cases = [
            SourceCase('Dir on 1st line, Negation and DIR-CONTENTS-MATCHER on 2nd line',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           instruction_arguments.NEGATION_ARGUMENT_STR + ' ' + EMPTINESS_CHECK_ARGUMENT,
                       ]),
                       source_assertion=asrt_source.source_is_at_end
                       ),
            SourceCase('Dir on 1st line, Negation and DIR-CONTENTS-MATCHER on 2nd line, followed by non-instr lines',
                       source=remaining_source_lines([
                           DIR_TO_CHECK,
                           instruction_arguments.NEGATION_ARGUMENT_STR,
                           EMPTINESS_CHECK_ARGUMENT,
                           '',
                           'following line',
                       ]),
                       source_assertion=asrt_source.is_at_beginning_of_line(4)
                       ),
        ]
        for case in cases:
            self._check_sub_test(case,
                                 PassOrFailOrHardErrorEnum.FAIL)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
