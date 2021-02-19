import unittest
from typing import List, Optional, Callable

from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.partial_execution.test_resources.basic import test__va, Arrangement, \
    result_is_pass
from exactly_lib_test.execution.partial_execution.test_resources.recording.phase_propagation import PosInPhase, \
    StepInfo, RecordingEntry
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_resources.actions import do_return__wo_args


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestDefaultEnvVarsIsAvailableInAllPhases(),
        TestEnvironVariablesAreNoneIfValueInConfigIsNone(),
        TestPropagationOfEnvironInSettings(),
    ])


class TestDefaultEnvVarsIsAvailableInAllPhases(unittest.TestCase):
    def runTest(self):
        default_environ = {'env_var_name': 'env var value'}

        recording_media = _empty_recording_media()
        expected_recordings = [
            RecordingEntry.from_settings(PhaseEnum.SETUP, None, default_environ),

            RecordingEntry.from_settings(PhaseEnum.BEFORE_ASSERT, None, default_environ),

            RecordingEntry.from_settings(PhaseEnum.ASSERT, None, default_environ),

            RecordingEntry.from_settings(PhaseEnum.CLEANUP, None, default_environ),
        ]

        helper = RecordingsHelper(recording_media)
        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recording_of_default_environ(PhaseEnum.SETUP),
                ),
            ],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [
                before_assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recording_of_default_environ(PhaseEnum.BEFORE_ASSERT),
                ),
            ],
            [
                assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recording_of_default_environ(PhaseEnum.ASSERT),
                ),
            ],
            [
                cleanup_phase_instruction_that(
                    main_initial_action=helper.action_for_recording_of_default_environ(PhaseEnum.CLEANUP),
                ),
            ],
        )
        null_actor = ActorThatRunsConstantActions()
        # ACT #
        test__va(
            self,
            test_case,
            Arrangement(
                actor=null_actor,
                default_environ_getter=do_return__wo_args(dict(default_environ))
            ),
            result_is_pass(),
        )
        self.assertEqual(expected_recordings,
                         recording_media,
                         'recordings')


class TestEnvironVariablesAreNoneIfValueInConfigIsNone(unittest.TestCase):
    def runTest(self):
        mb_dict__in_arrangement = None
        mb_dict__expected = None

        recording_media = _empty_recording_media()
        expected_recordings = [
            # setup #
            RecordingEntry.from_environment(PhaseEnum.SETUP, None,
                                            mb_dict__expected),
            RecordingEntry.from_settings(PhaseEnum.SETUP, None,
                                         mb_dict__expected),

            # act #
            RecordingEntry.from_environment(PhaseEnum.ACT, None,
                                            mb_dict__expected),

            # before-assert #
            RecordingEntry.from_environment(PhaseEnum.BEFORE_ASSERT, None,
                                            mb_dict__expected),
            RecordingEntry.from_settings(PhaseEnum.BEFORE_ASSERT, None,
                                         mb_dict__expected),

            # assert #
            RecordingEntry.from_environment(PhaseEnum.ASSERT, None,
                                            mb_dict__expected),
            RecordingEntry.from_settings(PhaseEnum.ASSERT, None,
                                         mb_dict__expected),

            # cleanup #
            RecordingEntry.from_environment(PhaseEnum.CLEANUP, None,
                                            mb_dict__expected),
            RecordingEntry.from_settings(PhaseEnum.CLEANUP, None,
                                         mb_dict__expected),
        ]

        helper = RecordingsHelper(recording_media)
        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.SETUP,
                                                                         None),
                ),
            ],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [
                before_assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.BEFORE_ASSERT,
                                                                         None),
                ),
            ],
            [
                assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.ASSERT,
                                                                         None),
                ),
            ],
            [
                cleanup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.CLEANUP,
                                                                         None),
                ),
            ],
        )
        # ACT #
        test__va(
            self,
            test_case,
            Arrangement(
                actor=_actor_that_records_values_of_environment(recording_media),
                environ=mb_dict__in_arrangement
            ),
            result_is_pass(),
        )
        self.assertEqual(expected_recordings,
                         recording_media,
                         'recordings')


class TestPropagationOfEnvironInSettings(unittest.TestCase):
    def runTest(self):
        var__initial = NameAndValue('initial_env_var', 'initial env var value')
        var__setup = NameAndValue('setup_env_var', 'setup env var value')
        var__before_assert = NameAndValue('before_assert_env_var', 'before_assert env var value')
        var__assert = NameAndValue('assert_env_var', 'assert env var value')
        var__cleanup = NameAndValue('cleanup_env_var', 'cleanup env var value')

        dict__initial = NameAndValue.as_dict([var__initial])
        dict__after_setup = NameAndValue.as_dict([var__initial, var__setup])
        dict__after_before_assert = NameAndValue.as_dict([var__initial,
                                                          var__setup,
                                                          var__before_assert])
        dict__after_assert = NameAndValue.as_dict([var__initial,
                                                   var__setup,
                                                   var__before_assert,
                                                   var__assert])
        dict__after_cleanup = NameAndValue.as_dict([var__initial,
                                                    var__setup,
                                                    var__before_assert,
                                                    var__assert,
                                                    var__cleanup])
        timeout__initial = 1
        timeout__after_setup = 2
        timeout__after_before_assert = 3
        timeout__after_assert = 4
        timeout__after_cleanup = 5

        recording_media = _empty_recording_media()
        expected_recordings = [
            # setup #
            RecordingEntry.from_environment(PhaseEnum.SETUP, PosInPhase.BEFORE_MODIFY,
                                            dict__initial,
                                            timeout__initial),
            RecordingEntry.from_settings(PhaseEnum.SETUP, PosInPhase.BEFORE_MODIFY,
                                         dict__initial,
                                         timeout__initial),

            RecordingEntry.from_environment(PhaseEnum.SETUP, PosInPhase.AFTER_MODIFY,
                                            dict__after_setup,
                                            timeout__after_setup),
            RecordingEntry.from_settings(PhaseEnum.SETUP, PosInPhase.AFTER_MODIFY,
                                         dict__after_setup,
                                         timeout__after_setup),

            # act #
            RecordingEntry.from_environment(PhaseEnum.ACT, None,
                                            dict__after_setup,
                                            timeout__after_setup),

            # before-assert #
            RecordingEntry.from_environment(PhaseEnum.BEFORE_ASSERT, PosInPhase.BEFORE_MODIFY,
                                            dict__after_setup,
                                            timeout__after_setup),
            RecordingEntry.from_settings(PhaseEnum.BEFORE_ASSERT, PosInPhase.BEFORE_MODIFY,
                                         dict__after_setup,
                                         timeout__after_setup),

            RecordingEntry.from_environment(PhaseEnum.BEFORE_ASSERT, PosInPhase.AFTER_MODIFY,
                                            dict__after_before_assert,
                                            timeout__after_before_assert),
            RecordingEntry.from_settings(PhaseEnum.BEFORE_ASSERT, PosInPhase.AFTER_MODIFY,
                                         dict__after_before_assert,
                                         timeout__after_before_assert),

            # assert #
            RecordingEntry.from_environment(PhaseEnum.ASSERT, PosInPhase.BEFORE_MODIFY,
                                            dict__after_before_assert,
                                            timeout__after_before_assert),
            RecordingEntry.from_settings(PhaseEnum.ASSERT, PosInPhase.BEFORE_MODIFY,
                                         dict__after_before_assert,
                                         timeout__after_before_assert),

            RecordingEntry.from_environment(PhaseEnum.ASSERT, PosInPhase.AFTER_MODIFY,
                                            dict__after_assert,
                                            timeout__after_assert),
            RecordingEntry.from_settings(PhaseEnum.ASSERT, PosInPhase.AFTER_MODIFY,
                                         dict__after_assert,
                                         timeout__after_assert),

            # cleanup #
            RecordingEntry.from_environment(PhaseEnum.CLEANUP, PosInPhase.BEFORE_MODIFY,
                                            dict__after_assert,
                                            timeout__after_assert),
            RecordingEntry.from_settings(PhaseEnum.CLEANUP, PosInPhase.BEFORE_MODIFY,
                                         dict__after_assert,
                                         timeout__after_assert),

            RecordingEntry.from_environment(PhaseEnum.CLEANUP, PosInPhase.AFTER_MODIFY,
                                            dict__after_cleanup,
                                            timeout__after_cleanup),
            RecordingEntry.from_settings(PhaseEnum.CLEANUP, PosInPhase.AFTER_MODIFY,
                                         dict__after_cleanup,
                                         timeout__after_cleanup),
        ]

        helper = RecordingsHelper(recording_media)
        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.SETUP,
                                                                         PosInPhase.BEFORE_MODIFY),
                ),
                setup_phase_instruction_that(
                    main_initial_action=ActionThatSetsVarInSettings(var__setup,
                                                                    timeout__after_setup).initial_action,
                ),
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.SETUP,
                                                                         PosInPhase.AFTER_MODIFY),
                ),
            ],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [
                before_assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.BEFORE_ASSERT,
                                                                         PosInPhase.BEFORE_MODIFY),
                ),
                before_assert_phase_instruction_that(
                    main_initial_action=ActionThatSetsVarInSettings(var__before_assert,
                                                                    timeout__after_before_assert).initial_action,
                ),
                before_assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.BEFORE_ASSERT,
                                                                         PosInPhase.AFTER_MODIFY),
                ),
            ],
            [
                assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.ASSERT,
                                                                         PosInPhase.BEFORE_MODIFY),
                ),
                assert_phase_instruction_that(
                    main_initial_action=ActionThatSetsVarInSettings(var__assert,
                                                                    timeout__after_assert).initial_action,
                ),
                assert_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.ASSERT,
                                                                         PosInPhase.AFTER_MODIFY),
                ),
            ],
            [
                cleanup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.CLEANUP,
                                                                         PosInPhase.BEFORE_MODIFY),
                ),
                cleanup_phase_instruction_that(
                    main_initial_action=ActionThatSetsVarInSettings(var__cleanup,
                                                                    timeout__after_cleanup).initial_action,
                ),
                cleanup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.CLEANUP,
                                                                         PosInPhase.AFTER_MODIFY),
                ),
            ],
        )
        # ACT #
        env_vars_in_arrangement__read_write = dict(dict__initial)
        test__va(
            self,
            test_case,
            Arrangement(
                actor=_actor_that_records_values_of_environment(recording_media),
                timeout_in_seconds=timeout__initial,
                environ=env_vars_in_arrangement__read_write,
            ),
            result_is_pass(),
        )
        self.assertEqual(expected_recordings,
                         recording_media,
                         'recordings')
        self.assertEqual(dict__initial,
                         env_vars_in_arrangement__read_write,
                         'env vars given to executor should not be modified')


def _empty_recording_media() -> List[RecordingEntry]:
    return []


class RecordingsHelper:
    def __init__(self,
                 recording_media: List[RecordingEntry],
                 ):
        self.recording_media = recording_media

    def action_for_recordings_for(self, phase: PhaseEnum, pos_in_phase: Optional[PosInPhase]) -> Callable:
        return RecordEnvVarsAndTimeout(phase, pos_in_phase, self.recording_media).call

    def action_for_recording_of_default_environ(self, phase: PhaseEnum,
                                                pos_in_phase: Optional[PosInPhase] = None) -> Callable:
        return RecordDefaultEnviron(phase, pos_in_phase, self.recording_media).call


def _act_phase_instructions_that_are_not_relevant_to_this_test() -> List[ActPhaseInstruction]:
    return [act_phase_instruction_with_source(LineSequence(1, ('line',)))]


class SetEnvironmentVariableInInstructionSettings:
    def __init__(self, val_var: NameAndValue[str]):
        self.val_var = val_var

    def call(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             *args):
        environ_before = settings.environ()
        assert environ_before is not None
        environ_before[self.val_var.name] = self.val_var.value


class RecordEnvVarsAndTimeout:
    def __init__(self,
                 phase: PhaseEnum,
                 pos_in_phase: Optional[PosInPhase],
                 recording_media: List[RecordingEntry],
                 ):
        self.phase = phase
        self.pos_in_phase = pos_in_phase
        self.recording_media = recording_media

    def call(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             *args):
        self.recording_media += [
            RecordingEntry(StepInfo.of_environment(self.phase, self.pos_in_phase),
                           environment.proc_exe_settings.environ,
                           environment.proc_exe_settings.timeout_in_seconds),
            RecordingEntry(StepInfo.of_settings(self.phase, self.pos_in_phase),
                           settings.environ(),
                           settings.timeout_in_seconds()),
        ]


class RecordDefaultEnviron:
    def __init__(self,
                 phase: PhaseEnum,
                 pos_in_phase: Optional[PosInPhase],
                 recording_media: List[RecordingEntry],
                 ):
        self.phase = phase
        self.pos_in_phase = pos_in_phase
        self.recording_media = recording_media

    def call(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             *args):
        self.recording_media += [
            RecordingEntry(StepInfo.of_settings(self.phase, self.pos_in_phase),
                           settings.default_environ_getter()),
        ]


def _actor_that_records_values_of_environment(recording_media: List[RecordingEntry]) -> Actor:
    return ActorThatRunsConstantActions(
        execute_initial_action=StepRecorderOfValuesFromEnvironment(PhaseEnum.ACT, None, recording_media).initial_action,
    )


class StepRecorderOfValuesFromEnvironment:
    def __init__(self,
                 phase: PhaseEnum,
                 pos_in_phase: Optional[PosInPhase],
                 recording_media: List[RecordingEntry],
                 ):
        self._phase = phase
        self._pos_in_phase = pos_in_phase
        self._recording_media = recording_media

    def initial_action(self, environment: InstructionEnvironmentForPostSdsStep, *args):
        self._recording_media.append(
            RecordingEntry(
                StepInfo.of_environment(self._phase, self._pos_in_phase),
                environment.proc_exe_settings.environ,
                environment.proc_exe_settings.timeout_in_seconds,
            )
        )


class ActionThatSetsVarInSettings:
    def __init__(self,
                 env_var: NameAndValue[str],
                 timeout: Optional[int],
                 ):
        self._env_var = env_var
        self._timeout = timeout

    def initial_action(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       settings: InstructionSettings,
                       *args):
        settings.set_timeout(self._timeout)

        if settings.environ() is None:
            settings.set_environ({})
        environ = settings.environ()
        assert environ is not None

        settings.environ()[self._env_var.name] = self._env_var.value


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
