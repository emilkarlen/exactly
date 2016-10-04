import pathlib

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor, ExitCodeOrHardError, ActSourceAndExecutor
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder


class ActSourceExecutorWrapperThatRecordsSteps(ActSourceExecutor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def validate_pre_eds(self,
                         source_setup: SourceSetup,
                         home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_PRE_EDS).record()
        return self.__wrapped.validate_pre_eds(source_setup, home_dir_path)

    def validate(self,
                 home_dir: pathlib.Path,
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_POST_SETUP).record()
        return self.__wrapped.validate(home_dir, source)

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        self.__recorder.recording_of(phase_step.ACT__PREPARE).record()
        return self.__wrapped.prepare(source_setup, home_dir_path, eds)

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__recorder.recording_of(phase_step.ACT__EXECUTE).record()
        return self.__wrapped.execute(source_setup,
                                      home_dir,
                                      eds,
                                      std_files)


def do_nothing():
    pass


class ActSourceExecutorWrapperWithActions(ActSourceExecutor):
    def __init__(self,
                 wrapped: ActSourceExecutor,
                 before_wrapped_validate=do_nothing,
                 before_wrapped_prepare=do_nothing,
                 before_wrapped_execute=do_nothing,
                 before_wrapped_validate_pre_eds=do_nothing):
        self.__wrapped = wrapped
        self.before_wrapped_validate = before_wrapped_validate
        self.before_wrapped_validate_pre_eds = before_wrapped_validate_pre_eds
        self.before_wrapped_prepare = before_wrapped_prepare
        self.before_wrapped_execute = before_wrapped_execute

    def validate_pre_eds(self,
                         source_setup: SourceSetup,
                         home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        self.before_wrapped_validate_pre_eds()
        return self.__wrapped.validate_pre_eds(source_setup, home_dir_path)

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        self.before_wrapped_validate()
        return self.__wrapped.validate(home_dir, source)

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        self.before_wrapped_prepare()
        return self.__wrapped.prepare(source_setup, home_dir_path, eds)

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.before_wrapped_execute()
        return self.__wrapped.execute(source_setup,
                                      home_dir,
                                      eds,
                                      std_files)


class ActSourceAndExecutorWrapperThatRecordsSteps(ActSourceAndExecutor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceAndExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def validate_pre_eds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_PRE_EDS).record()
        return self.__wrapped.validate_pre_eds(home_dir_path)

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_POST_SETUP).record()
        return self.__wrapped.validate_post_setup(home_and_eds)

    def prepare(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.__recorder.recording_of(phase_step.ACT__PREPARE).record()
        return self.__wrapped.prepare(home_and_eds, script_output_dir_path)

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__recorder.recording_of(phase_step.ACT__EXECUTE).record()
        return self.__wrapped.execute(home_and_eds, script_output_dir_path, std_files)
