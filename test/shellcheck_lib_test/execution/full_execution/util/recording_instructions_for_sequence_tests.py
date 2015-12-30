from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, \
    ConfigurationBuilder
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib_test.execution.test_resources.instruction_adapter import InternalInstruction


class ListElementRecorder:
    def __init__(self,
                 element_list: list,
                 element: str):
        self.recorder = element_list
        self.element = element

    def record(self):
        self.recorder.append(self.element)


class ListRecorder:
    def __init__(self):
        self.__element_list = []

    def recording_of(self, element: str) -> ListElementRecorder:
        return ListElementRecorder(self.__element_list, element)

    @property
    def recorded_elements(self) -> list:
        return self.__element_list


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
                      global_environment:  common.GlobalEnvironmentForPostEdsPhase) \
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
