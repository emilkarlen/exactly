import os
import re
import time
import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as step
from exactly_lib.execution.phase_step_identifiers.phase_step import SimplePhaseStep
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.basic import Result, test__va, dummy_act_phase_handling
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(
        TestThatWhenAnInstructionSetsAnEnvironmentVariableItShouldNotModifyTheVariablesOfTheWholeProcess)


class TestThatWhenAnInstructionSetsAnEnvironmentVariableItShouldNotModifyTheVariablesOfTheWholeProcess(
    unittest.TestCase):
    def test_set_environment_variable_in_phase_setup(self):
        recorder = _RecorderOfExistenceOfGlobalEnvVar(_unique_variable_name())

        test_case = partial_test_case_with_instructions(
            [setup_phase_instruction_that(
                main_initial_action=_Sequence([SetEnvironmentVariableViaInstructionArguments(recorder.variable_name),
                                               recorder.for_step(step.SETUP__MAIN)]),
                validate_post_setup_initial_action=recorder.for_step(step.SETUP__VALIDATE_POST_SETUP))],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [before_assert_phase_instruction_that(
                validate_post_setup_initial_action=recorder.for_step(step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=recorder.for_step(step.BEFORE_ASSERT__MAIN))],
            [assert_phase_instruction_that(
                validate_post_setup_initial_action=recorder.for_step(step.ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=recorder.for_step(step.ASSERT__MAIN))],
            [cleanup_phase_instruction_that(
                main_initial_action=recorder.for_step(step.CLEANUP__MAIN))],
        )
        test__va(
            self,
            test_case,
            _act_phase_handling_that_records_existence_of_var_in_global_env(recorder),
            AssertPhasesWhereTheEnvironmentVariableExistsInTheGlobalEnvironmentIEmpty(recorder.recorded_steps),
            is_keep_execution_directory_root=False)

    def test_set_environment_variable_in_phase_before_assert(self):
        recorder = _RecorderOfExistenceOfGlobalEnvVar(_unique_variable_name())

        test_case = partial_test_case_with_instructions(
            [],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [before_assert_phase_instruction_that(
                main_initial_action=_Sequence([SetEnvironmentVariableViaInstructionArguments(recorder.variable_name),
                                               recorder.for_step(step.BEFORE_ASSERT__MAIN)]))],
            [assert_phase_instruction_that(
                validate_post_setup_initial_action=recorder.for_step(step.ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=recorder.for_step(step.ASSERT__MAIN))],
            [cleanup_phase_instruction_that(
                main_initial_action=recorder.for_step(step.CLEANUP__MAIN))],
        )
        test__va(
            self,
            test_case,
            dummy_act_phase_handling(),
            AssertPhasesWhereTheEnvironmentVariableExistsInTheGlobalEnvironmentIEmpty(recorder.recorded_steps),
            is_keep_execution_directory_root=False)

    def test_set_environment_variable_in_phase_assert(self):
        recorder = _RecorderOfExistenceOfGlobalEnvVar(_unique_variable_name())

        test_case = partial_test_case_with_instructions(
            [],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [],
            [assert_phase_instruction_that(
                main_initial_action=_Sequence([SetEnvironmentVariableViaInstructionArguments(recorder.variable_name),
                                               recorder.for_step(step.ASSERT__MAIN)]))],
            [cleanup_phase_instruction_that(
                main_initial_action=recorder.for_step(step.CLEANUP__MAIN))],
        )
        test__va(
            self,
            test_case,
            dummy_act_phase_handling(),
            AssertPhasesWhereTheEnvironmentVariableExistsInTheGlobalEnvironmentIEmpty(recorder.recorded_steps),
            is_keep_execution_directory_root=False)

    def test_set_environment_variable_in_phase_cleanup(self):
        recorder = _RecorderOfExistenceOfGlobalEnvVar(_unique_variable_name())

        test_case = partial_test_case_with_instructions(
            [],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [],
            [],
            [cleanup_phase_instruction_that(
                main_initial_action=_Sequence([SetEnvironmentVariableViaInstructionArguments(recorder.variable_name),
                                               recorder.for_step(step.CLEANUP__MAIN)]))],
        )
        test__va(
            self,
            test_case,
            dummy_act_phase_handling(),
            AssertPhasesWhereTheEnvironmentVariableExistsInTheGlobalEnvironmentIEmpty(recorder.recorded_steps),
            is_keep_execution_directory_root=False)


def _act_phase_instructions_that_are_not_relevant_to_this_test():
    return [act_phase_instruction_with_source(LineSequence(1, ('line',)))]


def _unique_variable_name():
    return 'TEST_VAR_' + _time_stamp_string()


class _RecorderOfExistenceOfGlobalEnvVar:
    def __init__(self, environment_variable_name: str):
        self.variable_name = environment_variable_name
        self.recorded_steps = set()

    def for_step(self, phase_step: SimplePhaseStep):
        return AddPhaseToRecorderIfEnvironmentVariableIsSetForProcess(phase_step,
                                                                      self.recorded_steps,
                                                                      self.variable_name)


class _Sequence:
    def __init__(self, list_of_callable: list):
        self.list_of_callable = list_of_callable

    def __call__(self, *args, **kwargs):
        for fun in self.list_of_callable:
            fun(*args, **kwargs)


class SetEnvironmentVariableViaInstructionArguments:
    def __init__(self, variable_name: str):
        self.variable_name = variable_name

    def __call__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices,
                 *args, **kwargs):
        environment.environ[self.variable_name] = 'value that is not used by the test'


class AddPhaseToRecorderIfEnvironmentVariableIsSetForProcess:
    def __init__(self, phase_step: SimplePhaseStep, phases_that_contains_the_environment_variable: set,
                 variable_name: str):
        self.phase_step = phase_step
        self.phases_that_contains_the_environment_variable = phases_that_contains_the_environment_variable
        self.variable_name = variable_name

    def __call__(self, *args, **kwargs):
        if self.variable_name in os.environ:
            self.phases_that_contains_the_environment_variable.add(self.phase_step)


class AssertPhasesWhereTheEnvironmentVariableExistsInTheGlobalEnvironmentIEmpty(va.ValueAssertion):
    def __init__(self,
                 phases_that_contains_the_environment_variable: set):
        self.phases_that_contains_the_environment_variable = phases_that_contains_the_environment_variable

    def apply(self, put: unittest.TestCase,
              value: Result,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        msg = 'set of phases that have the environment variable in the global environment is expected to be empty'
        put.assertEqual(set(),
                        self.phases_that_contains_the_environment_variable,
                        msg)


def _act_phase_handling_that_records_existence_of_var_in_global_env(
        recorder: _RecorderOfExistenceOfGlobalEnvVar) -> ActPhaseHandling:
    return ActPhaseHandling(ActSourceAndExecutorConstructorThatRunsConstantActions(
        validate_pre_sds_initial_action=recorder.for_step(step.ACT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder.for_step(step.ACT__VALIDATE_POST_SETUP),
        prepare_initial_action=recorder.for_step(step.ACT__PREPARE),
        execute_initial_action=recorder.for_step(step.ACT__EXECUTE),
    ))


def _time_stamp_string() -> str:
    time_float = time.time()
    return re.sub(r'[^0-9]', '_', str(time_float))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
