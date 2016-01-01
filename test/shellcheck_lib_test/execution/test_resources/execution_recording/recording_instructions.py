from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, \
    ConfigurationBuilder
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib_test.execution.test_resources import instruction_adapter
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import ListElementRecorder, ListRecorder
from shellcheck_lib_test.execution.test_resources.instruction_adapter import InternalInstruction


class RecordingInstructions:
    def __init__(self, recorder: ListRecorder):
        self.recorder = recorder

    def new_anonymous_instruction(self, text: str) -> SetupPhaseInstruction:
        return AnonymousInternalInstructionThatRecordsStringInList(self.__recorder_of(text))

    def new_setup_instruction(self,
                              text_for_pre_validate: str,
                              text_for_execute: str,
                              text_for_post_validate: str) -> SetupPhaseInstruction:
        return SetupInstructionThatRecordsStringInList(self.__recorder_of(text_for_pre_validate),
                                                       self.__recorder_of(text_for_execute),
                                                       self.__recorder_of(text_for_post_validate))

    def new_act_instruction(self,
                            text_for_validate: str,
                            text_for_execute: str) -> ActPhaseInstruction:
        return ActInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                     self.__recorder_of(text_for_execute))

    def new_assert_instruction(self,
                               text_for_validate: str,
                               text_for_execute: str) -> AssertPhaseInstruction:
        return AssertInternalInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                                self.__recorder_of(text_for_execute))

    def new_cleanup_instruction(self, text: str) -> CleanupPhaseInstruction:
        return instruction_adapter.as_cleanup(
                InternalInstructionThatRecordsStringInList(self.__recorder_of(text)))

    def __recorder_of(self, element: str) -> ListElementRecorder:
        return self.recorder.recording_of(element)


class ActInstructionThatRecordsStringInList(ActPhaseInstruction):
    def __init__(self,
                 recorder_for_validate: ListElementRecorder,
                 recorder_for_execute: ListElementRecorder):
        self.__recorder_for_validate = recorder_for_validate
        self.__recorder_for_execute = recorder_for_execute

    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_validate.record()
        return sh.new_sh_success()

    def main(
            self,
            global_environment: common.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        self.__recorder_for_execute.record()
        return sh.new_sh_success()


class AnonymousInternalInstructionThatRecordsStringInList(AnonymousPhaseInstruction):
    def __init__(self,
                 recorder: ListElementRecorder):
        self.__recorder = recorder

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        self.__recorder.record()
        return sh.new_sh_success()


class SetupInstructionThatRecordsStringInList(SetupPhaseInstruction):
    def __init__(self,
                 recorder_for_pre_validate: ListElementRecorder,
                 recorder_for_execute: ListElementRecorder,
                 recorder_for_post_validate: ListElementRecorder):
        self.__recorder_for_pre_validate = recorder_for_pre_validate
        self.__recorder_for_execute = recorder_for_execute
        self.__recorder_for_post_validate = recorder_for_post_validate

    def pre_validate(self,
                     global_environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_pre_validate.record()
        return sh.new_sh_success()

    def main(self,
             os_services: OsServices,
             environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.__recorder_for_execute.record()
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_post_validate.record()
        return sh.new_sh_success()


class InternalInstructionThatRecordsStringInList(InternalInstruction):
    def __init__(self,
                 recorder: ListElementRecorder):
        self.__recorder = recorder

    def execute(self, phase_name: str,
                environment: common.GlobalEnvironmentForPostEdsPhase,
                os_services: OsServices):
        self.__recorder.record()


class AssertInternalInstructionThatRecordsStringInList(AssertPhaseInstruction):
    def __init__(self,
                 recorder_for_validate: ListElementRecorder,
                 recorder_for_execute: ListElementRecorder):
        self.__recorder_for_validate = recorder_for_validate
        self.__recorder_for_execute = recorder_for_execute

    def validate(self,
                 environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_validate.record()
        return svh.new_svh_success()

    def main(self, environment, os_services: ConfigurationBuilder) -> pfh.PassOrFailOrHardError:
        self.__recorder_for_execute.record()
        return pfh.new_pfh_pass()
