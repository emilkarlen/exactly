import pathlib

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.phase_setup import ActSourceExecutor, SourceSetup
from exactly_lib.test_case.phases.act.script_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder


class ActSourceExecutorWrapperThatRecordsSteps(ActSourceExecutor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__SCRIPT_VALIDATE).record()
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
        self.__recorder.recording_of(phase_step.ACT__SCRIPT_EXECUTE).record()
        return self.__wrapped.execute(source_setup,
                                      home_dir,
                                      eds,
                                      std_files)
