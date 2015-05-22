import pathlib

from shelltest.test_case.success_or_hard_error_construction import new_success
from shelltest.test_case import pass_or_fail_or_hard_error_construction
from shelltest.test_case import success_or_validation_hard_or_error_construction
from shelltest.test_case.instructions import SuccessOrHardError
from shelltest.test_case import instructions
from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure


class ListRecorder:
    def __init__(self,
                 recorder: list,
                 element: str):
        self.recorder = recorder
        self.element = element

    def record(self):
        self.recorder.append(self.element)


class ActInstructionThatRecordsStringInList(instructions.ActPhaseInstruction):
    def __init__(self,
                 recorder_for_validate: ListRecorder,
                 recorder_for_execute: ListRecorder):
        self.__recorder_for_validate = recorder_for_validate
        self.__recorder_for_execute = recorder_for_execute

    def validate(self, global_environment: instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_validate.record()
        return success_or_validation_hard_or_error_construction.new_success()

    def main(
            self,
            global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
            phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        self.__recorder_for_execute.record()
        return new_success()


class AnonymousInternalInstructionThatRecordsStringInList(instructions.AnonymousPhaseInstruction):
    def __init__(self,
                 recorder: ListRecorder):
        self.__recorder = recorder

    def main(self,
             global_environment,
             phase_environment: instructions.PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        self.__recorder.record()
        return new_success()


class SetupInstructionThatRecordsStringInList(instructions.SetupPhaseInstruction):
    def __init__(self,
                 recorder_for_pre_validate: ListRecorder,
                 recorder_for_execute: ListRecorder,
                 recorder_for_post_validate: ListRecorder):
        self.__recorder_for_pre_validate = recorder_for_pre_validate
        self.__recorder_for_execute = recorder_for_execute
        self.__recorder_for_post_validate = recorder_for_post_validate

    def pre_validate(self,
                     global_environment: instructions.GlobalEnvironmentForPreEdsStep) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_pre_validate.record()
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instructions.PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        self.__recorder_for_execute.record()
        return new_success()

    def post_validate(self,
                      global_environment:  instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_post_validate.record()
        return success_or_validation_hard_or_error_construction.new_success()


class SetupInstructionThatRecordsStringInRecordFile(instructions.SetupPhaseInstruction):
    def __init__(self,
                 text_for_execute: str,
                 test_for_post_validate: str):
        self.__text_for_execute = text_for_execute
        self.__text_for_post_validate = test_for_post_validate

    def pre_validate(self,
                     global_environment: instructions.GlobalEnvironmentForPreEdsStep) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instructions.PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__text_for_execute)
        return new_success()

    def post_validate(self,
                      global_environment:  instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__text_for_post_validate)
        return success_or_validation_hard_or_error_construction.new_success()


class InternalInstructionThatRecordsStringInRecordFile(instructions.InternalInstruction):
    def __init__(self,
                 text_for_execute):
        self.__text_for_execute = text_for_execute

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__text_for_execute)


class InternalInstructionThatRecordsStringInList(instructions.InternalInstruction):
    def __init__(self,
                 recorder: ListRecorder):
        self.__recorder = recorder

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        self.__recorder.record()


class ActInstructionThatGeneratesScriptThatRecordsStringInRecordFile(instructions.ActPhaseInstruction):
    def __init__(self,
                 string_for_script_gen: str):
        self.__string_for_script_gen = string_for_script_gen

    def validate(self, global_environment: instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(
            self,
            global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
            phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        phase_environment.append.raw_script_statements(
            append_line_to_record_file_statements(global_environment.execution_directory_structure,
                                                  self.__string_for_script_gen))
        return new_success()


class ActInstructionThatRecordsStringInRecordFile(instructions.ActPhaseInstruction):
    def __init__(self,
                 string_for_validation: str,
                 string_for_script_gen: str):
        self.__string_for_validation = string_for_validation
        self.__string_for_script_gen = string_for_script_gen

    def validate(self, global_environment: instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__string_for_validation)
        return success_or_validation_hard_or_error_construction.new_success()

    def main(
            self,
            global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
            phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__string_for_script_gen)
        return new_success()


class AssertInternalInstructionThatRecordsStringInList(instructions.AssertPhaseInstruction):
    def __init__(self,
                 recorder_for_validate: ListRecorder,
                 recorder_for_execute: ListRecorder):
        self.__recorder_for_validate = recorder_for_validate
        self.__recorder_for_execute = recorder_for_execute

    def validate(self,
                 global_environment: instructions.GlobalEnvironmentForPreEdsStep) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        self.__recorder_for_validate.record()
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment,
             phase_environment: instructions.PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        self.__recorder_for_execute.record()
        return pass_or_fail_or_hard_error_construction.new_success()


class AssertInstructionThatRecordsStringInRecordFile(instructions.AssertPhaseInstruction):
    def __init__(self,
                 string_for_validation: str,
                 string_for_script_gen: str):
        self.__string_for_validation = string_for_validation
        self.__string_for_script_gen = string_for_script_gen

    def validate(self, global_environment: instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__string_for_validation)
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__string_for_script_gen)
        return pass_or_fail_or_hard_error_construction.new_success()


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
