"""
Test of test-infrastructure: instruction_check.
"""
import functools
import os
import unittest

from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    act_phase_instruction_that
from exactly_lib_test.instructions.act.test_resources import instruction_check as sut
from exactly_lib_test.instructions.act.test_resources.instruction_check import SourceBuilderCheckInfo
from exactly_lib_test.instructions.test_resources import sh_check__va
from exactly_lib_test.instructions.test_resources import svh_check__va
from exactly_lib_test.test_resources import value_assertion as va
from exactly_lib_test.test_resources.execution.eds_contents_check__va import act_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.value_assertion_test import \
    TestException


class ConcreteTestCase(sut.TestCaseBase):
    def __init__(self):
        super().__init__()
        self.failureException = TestException


class TestCases(sut.TestCaseBase):
    def setUp(self):
        self.tc = ConcreteTestCase()

    def _check(self,
               instruction: ActPhaseInstruction,
               arrangement: sut.Arrangement,
               expectation: sut.Expectation):
        self.tc._check(instruction, arrangement, expectation)

    def test_successful_flow(self):
        self._check(
                SUCCESSFUL_INSTRUCTION,
                sut.Arrangement(),
                sut.is_success())

    def test_fail_due_to_unexpected_result_from__validate_pre_eds(self):
        with self.assertRaises(TestException):
            self._check(
                    SUCCESSFUL_INSTRUCTION,
                    sut.Arrangement(),
                    sut.Expectation(validation_pre_eds=svh_check__va.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result_from__validate_post_setup(self):
        with self.assertRaises(TestException):
            self._check(
                    SUCCESSFUL_INSTRUCTION,
                    sut.Arrangement(),
                    sut.Expectation(validation_post_setup=svh_check__va.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result__from_main(self):
        with self.assertRaises(TestException):
            self._check(
                    SUCCESSFUL_INSTRUCTION,
                    sut.Arrangement(),
                    sut.Expectation(main_result=sh_check__va.is_hard_error()),
            )

    def test_correct_argument_to_check_of_side_effects_on_source_builder(self):
        self._check(
                SUCCESSFUL_INSTRUCTION,
                sut.Arrangement(),
                sut.Expectation(main_side_effects_on_script_source=va.IsInstance(SourceBuilderCheckInfo)),
        )

    def test_fail_due_to_fail_of_side_effects_on_source_builder(self):
        with self.assertRaises(TestException):
            self._check(
                    SUCCESSFUL_INSTRUCTION,
                    sut.Arrangement(),
                    sut.Expectation(main_side_effects_on_script_source=va.fail('expected failure')),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(TestException):
            self._check(
                    SUCCESSFUL_INSTRUCTION,
                    sut.Arrangement(),
                    sut.Expectation(main_side_effects_on_files=act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main__and__validate_post_setup_is_act_dir(self):
        self._check(
                instruction_that_asserts_cwd_is_act_dir(self.tc),
                sut.Arrangement(),
                sut.is_success())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(TestException):
            self._check(
                    SUCCESSFUL_INSTRUCTION,
                    sut.Arrangement(),
                    sut.Expectation(home_and_eds=va.IsInstance(bool)),
            )


SUCCESSFUL_INSTRUCTION = act_phase_instruction_that()


def instruction_that_asserts_cwd_is_act_dir(put: unittest.TestCase):
    def do_main(ret_val, glob_env, phase_env):
        cwd = os.getcwd()
        put.assertEqual(str(glob_env.eds.act_dir),
                        cwd,
                        'Current Directory')
        return ret_val

    def do_post_setup(ret_val, glob_env: GlobalEnvironmentForPostEdsPhase):
        cwd = os.getcwd()
        put.assertEqual(str(glob_env.eds.act_dir),
                        cwd,
                        'Current Directory')
        return ret_val

    return act_phase_instruction_that(
            validate_post_setup=functools.partial(do_post_setup, svh.new_svh_success()),
            main=functools.partial(do_main, sh.new_sh_success()))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
