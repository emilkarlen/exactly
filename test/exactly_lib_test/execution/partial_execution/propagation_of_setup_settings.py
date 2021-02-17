import unittest
from typing import List, Optional, Callable, Mapping, Dict

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.partial_execution.test_resources.basic import test__va, Arrangement, \
    result_is_pass
from exactly_lib_test.execution.partial_execution.test_resources.recording.phase_propagation import PosInPhase, \
    StepInfo, RecordingEntry
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInitializationFromEnvVarsOfExeConfig(),
        TestPropagationOfModifiedEnvVars(),
    ])


class TestInitializationFromEnvVarsOfExeConfig(unittest.TestCase):
    def runTest(self):
        default_environ_cases = [
            NameAndValue(
                'None',
                None
            ),
            NameAndValue(
                'not None',
                {'env_var_name': 'env var value'}
            ),
        ]
        for default_environ_case in default_environ_cases:
            with self.subTest(default_environ_case.name):
                self._check_defaults(default_environ_case.value)

    def _check_defaults(self, default_environ: Optional[Mapping[str, str]]):
        recording_media = _empty_recording_media()
        expected_recordings = [
            # setup #
            RecordingEntry.from_settings(PhaseEnum.SETUP, None, default_environ),
            # act #
            RecordingEntry.from_settings(PhaseEnum.ACT, None, default_environ),
        ]

        helper = RecordingsHelper(recording_media)
        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.SETUP, None),
                ),
            ],
        )
        actor_that_records_env_vars_of_act_exe_input = ActorThatRunsConstantActions(
            execute_initial_action=helper.actor_action_for_recording_environ_of_act_exe_input,
        )
        # ACT #
        test__va(
            self,
            test_case,
            Arrangement(
                actor=actor_that_records_env_vars_of_act_exe_input,
                environ=default_environ,
            ),
            result_is_pass(),
        )
        self.assertEqual(expected_recordings,
                         recording_media,
                         'recordings')


class TestPropagationOfModifiedEnvVars(unittest.TestCase):
    def runTest(self):
        default_environ = None
        modified_environ = {'modified_var': 'val of modified var'}

        recording_media = _empty_recording_media()
        expected_recordings = [
            # setup #
            RecordingEntry.from_settings(PhaseEnum.SETUP, PosInPhase.BEFORE_MODIFY, default_environ),
            RecordingEntry.from_settings(PhaseEnum.SETUP, PosInPhase.AFTER_MODIFY, modified_environ),
            # act #
            RecordingEntry.from_settings(PhaseEnum.ACT, None, modified_environ),
        ]

        helper = RecordingsHelper(recording_media)
        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.SETUP, PosInPhase.BEFORE_MODIFY),
                ),
                setup_phase_instruction_that(
                    main_initial_action=ActionThatSetsSettings(dict(modified_environ)).initial_action,
                ),
                setup_phase_instruction_that(
                    main_initial_action=helper.action_for_recordings_for(PhaseEnum.SETUP, PosInPhase.AFTER_MODIFY),
                ),
            ],
        )
        actor_that_records_env_vars_of_act_exe_input = ActorThatRunsConstantActions(
            execute_initial_action=helper.actor_action_for_recording_environ_of_act_exe_input,
        )
        # ACT #
        test__va(
            self,
            test_case,
            Arrangement(
                actor=actor_that_records_env_vars_of_act_exe_input,
                environ=default_environ,
            ),
            result_is_pass(),
        )
        self.assertEqual(expected_recordings,
                         recording_media,
                         'recordings')


def _empty_recording_media() -> List[RecordingEntry]:
    return []


class ActionThatSetsSettings:
    def __init__(self, environ: Dict[str, str]):
        self._environ = environ

    def initial_action(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       instruction_settings: InstructionSettings,
                       os_services: OsServices,
                       setup_settings: SetupSettingsBuilder,
                       ):
        setup_settings.environ = self._environ


class RecordingsHelper:
    def __init__(self,
                 recording_media: List[RecordingEntry],
                 ):
        self.recording_media = recording_media

    def action_for_recordings_for(self, phase: PhaseEnum, pos_in_phase: Optional[PosInPhase]) -> Callable:
        return RecordEnvironOfSetupSettings(phase, pos_in_phase, self.recording_media).call

    def actor_action_for_recording_environ_of_act_exe_input(
            self,
            instruction_environment: InstructionEnvironmentForPostSdsStep,
            atc_input: AtcExecutionInput,
            std_output_files: StdOutputFiles,
    ):
        self.recording_media.append(
            RecordingEntry.from_settings(PhaseEnum.ACT,
                                         None,
                                         atc_input.environ)
        )


class RecordEnvironOfSetupSettings:
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
             instruction_settings: InstructionSettings,
             os_services: OsServices,
             setup_settings: SetupSettingsBuilder,
             ):
        self.recording_media += [
            RecordingEntry(StepInfo.of_settings(self.phase, self.pos_in_phase),
                           setup_settings.environ),
        ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
