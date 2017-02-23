"""
Test of test-infrastructure: instruction_check.
"""
import functools
import os
import unittest

from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionParser
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    before_assert_phase_instruction_that
from exactly_lib_test.instructions.before_assert.test_resources import instruction_check as sut
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.instructions.test_resources.test_of_test_framework_utils import single_line_sourceInstrDesc
from exactly_lib_test.test_resources.execution.sds_check.sds_contents_check import act_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_test import TestException


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCases)


class ConcreteTestCase(sut.TestCaseBase):
    def __init__(self):
        super().__init__()
        self.failureException = TestException


class TestCases(sut.TestCaseBase):
    def setUp(self):
        self.tc = ConcreteTestCase()

    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: sut.Expectation):
        self.tc._check(parser, source, arrangement, expectation)

    def test_successful_flow(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_sourceInstrDesc(),
            sut.arrangement(),
            sut.is_success())

    def test_fail_due_to_unexpected_result_from__validate_pre_sds(self):
        with self.assertRaises(TestException):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_sourceInstrDesc(),
                sut.arrangement(),
                sut.Expectation(validation_pre_sds=svh_check.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result_from__validate_post_setup(self):
        with self.assertRaises(TestException):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_sourceInstrDesc(),
                sut.arrangement(),
                sut.Expectation(validation_post_setup=svh_check.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result__from_main(self):
        with self.assertRaises(TestException):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_sourceInstrDesc(),
                sut.arrangement(),
                sut.Expectation(main_result=sh_check.is_hard_error()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(TestException):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_sourceInstrDesc(),
                sut.arrangement(),
                sut.Expectation(main_side_effects_on_files=act_dir_contains_exactly(
                    DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main__and__validate_post_setup_is_act_dir(self):
        self._check(
            test_misc.ParserThatGives(instruction_that_asserts_cwd_is_act_dir(self.tc)),
            single_line_sourceInstrDesc(),
            sut.arrangement(),
            sut.is_success())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(TestException):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_sourceInstrDesc(),
                sut.arrangement(),
                sut.Expectation(home_and_sds=va.IsInstance(bool)),
            )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = test_misc.ParserThatGives(before_assert_phase_instruction_that())


def instruction_that_asserts_cwd_is_act_dir(put: unittest.TestCase):
    def do_assert_cwd_is_act_dir(ret_val, environment: InstructionEnvironmentForPostSdsStep, *args):
        cwd = os.getcwd()
        put.assertEqual(str(environment.sds.act_dir),
                        cwd,
                        'Current Directory')
        return ret_val

    return before_assert_phase_instruction_that(
        validate_post_setup=functools.partial(do_assert_cwd_is_act_dir, svh.new_svh_success()),
        main=functools.partial(do_assert_cwd_is_act_dir, sh.new_sh_success()))


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
