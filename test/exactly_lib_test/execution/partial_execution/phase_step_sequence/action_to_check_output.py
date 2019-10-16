import os
import unittest
from typing import Optional

from exactly_lib.actors.source_interpreter import python3
from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.os_services import DEFAULT_ATC_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.result import sh
from exactly_lib.util.line_source import LineSequence, single_line_sequence
from exactly_lib.util.std import StdOutputFiles
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList, \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test, sandbox_root_name_resolver
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import ActorThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import \
    PRE_SDS_VALIDATION_STEPS__ONCE, SYMBOL_VALIDATION_STEPS__ONCE
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_SDS_VALIDATION_STEPS__TWICE, \
    SYMBOL_VALIDATION_STEPS__TWICE
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForNoFailure
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForPhaseFailure
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.test_actions import execute_action_that_raises
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.files.capture_out_files import capture_stdout_err
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailure),
        unittest.makeSuite(TestSuccess),
    ])


class Arrangement:
    def __init__(self,
                 test_case: TestCaseGeneratorForExecutionRecording,
                 actor: Actor,
                 timeout_in_seconds: Optional[int] = None):
        self.test_case_generator = test_case
        self.actor = actor
        self.timeout_in_seconds = timeout_in_seconds


def arr_for_py3_source(test_case: TestCaseGeneratorForExecutionRecording,
                       timeout_in_seconds: Optional[int] = None) -> Arrangement:
    return Arrangement(test_case,
                       python3.new_actor(),
                       timeout_in_seconds)


class Expectation:
    def __init__(self,
                 result: ValueAssertion[PartialExeResult],
                 atc_stdout_output: ValueAssertion[str],
                 atc_stderr_output: ValueAssertion[str],
                 step_recordings: list,
                 ):
        self.result = result
        self.atc_stdout_output = atc_stdout_output
        self.atc_stderr_output = atc_stderr_output
        self.step_recordings = step_recordings


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation):
    actor = ActorThatRecordsSteps(
        arrangement.test_case_generator.recorder,
        arrangement.actor)

    def action(std_files: StdOutputFiles) -> PartialExeResult:
        exe_conf = ExecutionConfiguration(dict(os.environ),
                                          DEFAULT_ATC_OS_PROCESS_EXECUTOR,
                                          sandbox_root_name_resolver.for_test(),
                                          exe_atc_and_skip_assertions=std_files)
        with home_directory_structure() as hds:
            conf_phase_values = ConfPhaseValues(actor,
                                                hds,
                                                timeout_in_seconds=arrangement.timeout_in_seconds)
            return sut.execute(arrangement.test_case_generator.test_case,
                               exe_conf,
                               conf_phase_values,
                               setup.default_settings(),
                               False,
                               )

    out_files, partial_result = capture_stdout_err(action)

    expectation.result.apply_with_message(put, partial_result,
                                          'partial result')
    put.assertEqual(expectation.step_recordings,
                    arrangement.test_case_generator.recorder.recorded_elements,
                    'steps')
    expectation.atc_stdout_output.apply_with_message(put, out_files.out,
                                                     'stdout')
    expectation.atc_stderr_output.apply_with_message(put, out_files.err,
                                                     'stderr')


class TestCaseBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self,
              arrangement,
              expectation)


class TestSuccess(TestCaseBase):
    def test(self):
        for expected_exit_code in [0, 69]:
            py_pgm_setup = PyProgramSetup('the output to stdout',
                                          'the output to stderr',
                                          expected_exit_code)
            with self.subTest(expected_exit_code=expected_exit_code):
                self._check(
                    arr_for_py3_source(TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr(
                        act_phase_source=py_pgm_setup.as_line_sequence()
                    ),
                    ),
                    Expectation(
                        asrt_result.matches2(
                            None,
                            asrt_result.has_sds(),
                            asrt_result.has_action_to_check_outcome_with_exit_code(py_pgm_setup.exit_code),
                            ExpectedFailureForNoFailure(),
                        ),
                        atc_stdout_output=asrt.equals(py_pgm_setup.stdout_output),
                        atc_stderr_output=asrt.equals(py_pgm_setup.stderr_output),
                        step_recordings=
                        [phase_step.ACT__PARSE] +

                        SYMBOL_VALIDATION_STEPS__TWICE +

                        PRE_SDS_VALIDATION_STEPS__TWICE +

                        [phase_step.SETUP__MAIN,
                         phase_step.SETUP__MAIN,

                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.ACT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                         ],
                    ))


class TestFailure(TestCaseBase):
    def test_hard_error_in_setup_main_step(self):
        py_pgm_setup = PyProgramSetup('some output to stdout',
                                      'some output to stderr',
                                      72)
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr(
            act_phase_source=py_pgm_setup.as_line_sequence()) \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error__str('hard error msg from setup'))))
        self._check(
            arr_for_py3_source(test_case),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.SETUP__MAIN,
                        test_case.the_extra(PartialPhase.SETUP)[0].source,
                        'hard error msg from setup'),
                ),
                atc_stdout_output=asrt.equals(''),
                atc_stderr_output=asrt.equals(''),
                step_recordings=
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__TWICE +
                PRE_SDS_VALIDATION_STEPS__TWICE +
                [phase_step.SETUP__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_implementation_error_in_act_execute(self):
        test_case = _single_successful_instruction_in_each_phase(single_line_sequence(72, 'ignored'))
        self._check(
            Arrangement(test_case,
                        ActorThatRunsConstantActions(
                            execute_action=execute_action_that_raises(
                                test.ImplementationErrorTestException()))),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.IMPLEMENTATION_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__EXECUTE,
                                         test.ImplementationErrorTestException)
                                     ),
                atc_stdout_output=asrt.equals(''),
                atc_stderr_output=asrt.equals(''),
                step_recordings=
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                 ],
            ))

    def test_timeout_in_action_to_check(self):
        stdout_before_sleep = 'some output on stdout before going into sleep'
        stderr_before_sleep = 'some output on stderr before going into sleep'

        py_pgm_line_sequence = py_pgm_with_stdout_stderr_and_sleep_in_between(
            stdout_output_before_sleep=stdout_before_sleep,
            stderr_output_before_sleep=stderr_before_sleep,
            stdout_output_after_sleep='more stdout output after sleep',
            stderr_output_after_sleep='more stderr output after sleep',
            sleep_seconds=3,
            exit_code=72)
        test_case = _single_successful_instruction_in_each_phase(
            act_phase_source=py_pgm_line_sequence)
        self._check(
            arr_for_py3_source(test_case,
                               timeout_in_seconds=1),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure(
                                         phase_step.ACT__EXECUTE,
                                         asrt.anything_goes())
                                     ),
                atc_stdout_output=asrt.equals(stdout_before_sleep),
                atc_stderr_output=asrt.equals(stderr_before_sleep),
                step_recordings=
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__ONCE +

                PRE_SDS_VALIDATION_STEPS__ONCE +

                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                 ],
            ))

    def test_hard_error_in_cleanup_main_step(self):
        py_pgm_setup = PyProgramSetup('some output to stdout',
                                      'some output to stderr',
                                      72)
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr(
            act_phase_source=py_pgm_setup.as_line_sequence()) \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error__str('hard error msg from CLEANUP'))))
        self._check(
            arr_for_py3_source(test_case),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(py_pgm_setup.exit_code),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CLEANUP__MAIN,
                        test_case.the_extra(PartialPhase.CLEANUP)[0].source,
                        'hard error msg from CLEANUP'),
                ),
                atc_stdout_output=asrt.equals(py_pgm_setup.stdout_output),
                atc_stderr_output=asrt.equals(py_pgm_setup.stderr_output),
                step_recordings=
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
                PRE_SDS_VALIDATION_STEPS__TWICE +
                [phase_step.SETUP__MAIN,
                 phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                 ],
            ))


def _single_successful_instruction_in_each_phase(act_phase_source: LineSequence
                                                 ) -> TestCaseGeneratorForExecutionRecording:
    return TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList(act_phase_source=act_phase_source)


class PyProgramSetup:
    def __init__(self,
                 stdout_output: str,
                 stderr_output: str,
                 exit_code: int
                 ):
        self.stdout_output = stdout_output
        self.stderr_output = stderr_output
        self.exit_code = exit_code

    def py_source(self) -> str:
        return py_programs.py_pgm_with_stdout_stderr_exit_code(self.stdout_output,
                                                               self.stderr_output,
                                                               self.exit_code)

    def as_line_sequence(self) -> LineSequence:
        return LineSequence(72, self.py_source().splitlines())


def py_pgm_with_stdout_stderr_and_sleep_in_between(stdout_output_before_sleep: str,
                                                   stderr_output_before_sleep: str,
                                                   stdout_output_after_sleep: str,
                                                   stderr_output_after_sleep: str,
                                                   sleep_seconds: int,
                                                   exit_code: int) -> LineSequence:
    py_src = py_programs.py_pgm_with_stdout_stderr_and_sleep_in_between(
        stdout_output_before_sleep,
        stderr_output_before_sleep,
        stdout_output_after_sleep,
        stderr_output_after_sleep,
        sleep_seconds,
        exit_code,
    )

    return LineSequence(69, py_src.splitlines())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
