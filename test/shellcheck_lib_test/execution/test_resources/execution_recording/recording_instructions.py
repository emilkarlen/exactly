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
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import ListElementRecorder, ListRecorder
from shellcheck_lib_test.execution.test_resources.instruction_adapter import InternalInstruction
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import cleanup_phase_instruction_that, \
    assert_phase_instruction_that


class RecordingInstructions:
    def __init__(self, recorder: ListRecorder):
        self.recorder = recorder

    def new_anonymous_instruction(self, value) -> SetupPhaseInstruction:
        return AnonymousInternalInstructionThatRecordsStringInList(self.__recorder_of(value))

    def new_setup_instruction(self,
                              value_for_pre_validate,
                              value_for_execute,
                              value_for_post_validate) -> SetupPhaseInstruction:
        return SetupInstructionThatRecordsStringInList(self.__recorder_of(value_for_pre_validate),
                                                       self.__recorder_of(value_for_execute),
                                                       self.__recorder_of(value_for_post_validate))

    def new_act_instruction(self,
                            value_for_validate_pre_eds,
                            value_for_validate,
                            value_for_execute) -> ActPhaseInstruction:
        return ActInstructionThatRecordsStringInList(self.__recorder_of(value_for_validate_pre_eds),
                                                     self.__recorder_of(value_for_validate),
                                                     self.__recorder_of(value_for_execute))

    def new_assert_instruction(self,
                               value_for_validate_pre_eds,
                               value_for_validate,
                               value_for_execute) -> AssertPhaseInstruction:
        return assert_instruction_that_records(self.__recorder_of(value_for_validate_pre_eds),
                                               self.__recorder_of(value_for_validate),
                                               self.__recorder_of(value_for_execute))

    def new_cleanup_instruction(self,
                                value_for_validate_pre_eds,
                                value_for_main) -> CleanupPhaseInstruction:
        return cleanup_instruction_that_records(self.__recorder_of(value_for_validate_pre_eds),
                                                self.__recorder_of(value_for_main))

    def __recorder_of(self, element) -> ListElementRecorder:
        return self.recorder.recording_of(element)


class ActInstructionThatRecordsStringInList(ActPhaseInstruction):
    def __init__(self,
                 recorder_for_validate_pre_eds: ListElementRecorder,
                 recorder_for_validate: ListElementRecorder,
                 recorder_for_execute: ListElementRecorder):
        self.__recorder_for_validate_pre_eds = recorder_for_validate_pre_eds
        self.__recorder_for_validate = recorder_for_validate
        self.__recorder_for_execute = recorder_for_execute

    def validate_pre_eds(self,
                         environment: common.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_validate_pre_eds.record()
        return svh.new_svh_success()

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

    def execute(self, phase_name,
                environment: common.GlobalEnvironmentForPostEdsPhase,
                os_services: OsServices):
        self.__recorder.record()


def assert_instruction_that_records(recorder_for_validate_pre_eds: ListElementRecorder,
                                    recorder_for_validate: ListElementRecorder,
                                    recorder_for_main: ListElementRecorder) -> AssertPhaseInstruction:
    return assert_phase_instruction_that(validate_pre_eds=_do_record_and_return_svh(recorder_for_validate_pre_eds),
                                         validate=_do_record_and_return_svh(recorder_for_validate),
                                         main=_do_record_and_return(recorder_for_main,
                                                                    pfh.new_pfh_pass()))


def cleanup_instruction_that_records(recorder_for_pre_validate: ListElementRecorder,
                                     recorder_for_main: ListElementRecorder) -> CleanupPhaseInstruction:
    return cleanup_phase_instruction_that(do_validate_pre_eds=_do_record_and_return_svh(recorder_for_pre_validate),
                                          do_main=_do_record_and_return_sh(recorder_for_main))


def _do_record_and_return_sh(recorder: ListElementRecorder):
    return _do_record_and_return(recorder, sh.new_sh_success())


def _do_record_and_return_svh(recorder: ListElementRecorder):
    return _do_record_and_return(recorder, svh.new_svh_success())


def _do_record_and_return(recorder: ListElementRecorder,
                          return_value):
    def ret_val():
        recorder.record()
        return return_value

    return ret_val
