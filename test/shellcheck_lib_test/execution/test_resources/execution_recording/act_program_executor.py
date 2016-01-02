import pathlib

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.std import StdFiles
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder


class ActProgramExecutorWrapperThatRecordsSteps(ActProgramExecutor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActProgramExecutor,
                 validate_test_action,
                 execute_test_action):
        self.__recorder = recorder
        self.__wrapped = wrapped
        self.__validate_test_action = validate_test_action
        self.__execute_test_action = execute_test_action

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT_SCRIPT_VALIDATE).record()
        test_action_result = self.__validate_test_action()
        if not test_action_result.is_success:
            return test_action_result
        return self.__wrapped.validate(home_dir, source)

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        self.__wrapped.prepare(source_setup, home_dir_path, eds)

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> int:
        self.__recorder.recording_of(phase_step.ACT_SCRIPT_EXECUTE).record()
        self.__execute_test_action()
        return self.__wrapped.execute(source_setup,
                                      home_dir,
                                      eds,
                                      std_files)
