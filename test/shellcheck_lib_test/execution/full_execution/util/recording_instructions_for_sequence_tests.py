import pathlib

from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction import common
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.test_case.instruction.sections.act import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.instruction.sections.anonymous import AnonymousPhaseInstruction, \
    ConfigurationBuilder
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib_test.execution.util.instruction_adapter import InternalInstruction

class ListRecorder:
    def __init__(self,
                 recorder: list,
                 element: str):
        self.recorder = recorder
        self.element = element

    def record(self):
        self.recorder.append(self.element)


class ActInstructionThatRecordsStringInList(ActPhaseInstruction):
    def __init__(self,
                 recorder_for_validate: ListRecorder,
                 recorder_for_execute: ListRecorder):
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
                 recorder: ListRecorder):
        self.__recorder = recorder

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        self.__recorder.record()
        return sh.new_sh_success()


class SetupInstructionThatRecordsStringInList(SetupPhaseInstruction):
    def __init__(self,
                 recorder_for_pre_validate: ListRecorder,
                 recorder_for_execute: ListRecorder,
                 recorder_for_post_validate: ListRecorder):
        self.__recorder_for_pre_validate = recorder_for_pre_validate
        self.__recorder_for_execute = recorder_for_execute
        self.__recorder_for_post_validate = recorder_for_post_validate

    def pre_validate(self,
                     global_environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_pre_validate.record()
        return sh.new_sh_success()

    def main(self,
             global_environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.__recorder_for_execute.record()
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment:  common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_post_validate.record()
        return sh.new_sh_success()


class SetupInstructionThatRecordsStringInRecordFile(
    SetupPhaseInstruction):
    def __init__(self,
                 text_for_execute: str,
                 test_for_post_validate: str):
        self.__text_for_execute = text_for_execute
        self.__text_for_post_validate = test_for_post_validate

    def pre_validate(self,
                     global_environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return sh.new_sh_success()

    def main(self,
             global_environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__text_for_execute)
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment:  common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__text_for_post_validate)
        return sh.new_sh_success()


class InternalInstructionThatRecordsStringInRecordFile(InternalInstruction):
    def __init__(self,
                 text_for_execute):
        self.__text_for_execute = text_for_execute

    def execute(self, phase_name: str,
                environment: common.GlobalEnvironmentForPostEdsPhase,
                os_services: OsServices):
        append_line_to_record_file(environment.execution_directory_structure,
                                   self.__text_for_execute)


class InternalInstructionThatRecordsStringInList(InternalInstruction):
    def __init__(self,
                 recorder: ListRecorder):
        self.__recorder = recorder

    def execute(self, phase_name: str,
                environment: common.GlobalEnvironmentForPostEdsPhase,
                os_services: OsServices):
        self.__recorder.record()


class ActInstructionThatGeneratesScriptThatRecordsStringInRecordFile(ActPhaseInstruction):
    def __init__(self,
                 string_for_script_gen: str):
        self.__string_for_script_gen = string_for_script_gen

    def validate(self,
                 environment: common.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return sh.new_sh_success()

    def main(
            self,
            global_environment: common.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        phase_environment.append.raw_script_statements(
            append_line_to_record_file_statements(global_environment.execution_directory_structure,
                                                  self.__string_for_script_gen))
        return sh.new_sh_success()


class ActInstructionThatRecordsStringInRecordFile(ActPhaseInstruction):
    def __init__(self,
                 string_for_validation: str,
                 string_for_script_gen: str):
        self.__string_for_validation = string_for_validation
        self.__string_for_script_gen = string_for_script_gen

    def validate(self,
                 environment: common.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        append_line_to_record_file(environment.execution_directory_structure,
                                   self.__string_for_validation)
        return sh.new_sh_success()

    def main(
            self,
            global_environment: common.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__string_for_script_gen)
        return sh.new_sh_success()


class AssertInternalInstructionThatRecordsStringInList(AssertPhaseInstruction):
    def __init__(self,
                 recorder_for_validate: ListRecorder,
                 recorder_for_execute: ListRecorder):
        self.__recorder_for_validate = recorder_for_validate
        self.__recorder_for_execute = recorder_for_execute

    def validate(self,
                 global_environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_validate.record()
        return svh.new_svh_success()

    def main(self, environment, os_services: ConfigurationBuilder) -> pfh.PassOrFailOrHardError:
        self.__recorder_for_execute.record()
        return pfh.new_pfh_pass()


class AssertInstructionThatRecordsStringInRecordFile(AssertPhaseInstruction):
    def __init__(self,
                 string_for_validation: str,
                 string_for_script_gen: str):
        self.__string_for_validation = string_for_validation
        self.__string_for_script_gen = string_for_script_gen

    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__string_for_validation)
        return sh.new_sh_success()

    def main(self, environment: common.GlobalEnvironmentForPostEdsPhase,
             os_services: PhaseEnvironmentForScriptGeneration) -> pfh.PassOrFailOrHardError:
        append_line_to_record_file(environment.execution_directory_structure,
                                   self.__string_for_script_gen)
        return pfh.new_pfh_pass()


RECORD_FILE_BASE_NAME = 'recording.txt'


def record_file_path(eds: ExecutionDirectoryStructure) -> pathlib.Path:
    return eds.root_dir / RECORD_FILE_BASE_NAME


def record_file_contents_from_lines(lines: list) -> str:
    return '\n'.join(lines) + '\n'


def append_line_to_record_file(eds: ExecutionDirectoryStructure,
                               line: str):
    append_line_to_file(record_file_path(eds), line)


def append_line_to_record_file_statements(eds: ExecutionDirectoryStructure,
                                          line: str) -> list:
    return [
        'with open(\'%s\', \'a\') as f:' % (str(record_file_path(eds))),
        '  f.write(\'%s\')' % (line + '\\n'),
    ]


def append_line_to_file(file_path: pathlib.Path,
                        line: str):
    with open(str(file_path), 'a') as f:
        f.write(line + '\n')
