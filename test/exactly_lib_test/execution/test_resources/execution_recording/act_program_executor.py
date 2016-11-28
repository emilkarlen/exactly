import pathlib

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError, ActSourceAndExecutor, \
    ActSourceAndExecutorConstructor, new_eh_exit_code, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import HomeAndSds, InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder


def do_nothing():
    pass


class ActSourceAndExecutorThatJustReturnsSuccess(ActSourceAndExecutor):
    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self, home_and_sds: HomeAndSds) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def prepare(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return new_eh_exit_code(0)


class ActSourceAndExecutorWrapperThatRecordsSteps(ActSourceAndExecutor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceAndExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_PRE_SDS).record()
        return self.__wrapped.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_POST_SETUP).record()
        return self.__wrapped.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.__recorder.recording_of(phase_step.ACT__PREPARE).record()
        return self.__wrapped.prepare(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__recorder.recording_of(phase_step.ACT__EXECUTE).record()
        return self.__wrapped.execute(environment, script_output_dir_path, std_files)


class ActSourceAndExecutorWrapperConstructorThatRecordsSteps(ActSourceAndExecutorConstructor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceAndExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        return ActSourceAndExecutorWrapperThatRecordsSteps(self.__recorder, self.__wrapped)


class ActSourceAndExecutorWrapperWithActions(ActSourceAndExecutor):
    def __init__(self,
                 wrapped: ActSourceAndExecutor,
                 before_wrapped_validate=do_nothing,
                 before_wrapped_prepare=do_nothing,
                 before_wrapped_execute=do_nothing,
                 before_wrapped_validate_pre_sds=do_nothing
                 ):
        self.__wrapped = wrapped
        self.before_wrapped_validate = before_wrapped_validate
        self.before_wrapped_validate_pre_sds = before_wrapped_validate_pre_sds
        self.before_wrapped_prepare = before_wrapped_prepare
        self.before_wrapped_execute = before_wrapped_execute

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.before_wrapped_validate_pre_sds(environment)
        return self.__wrapped.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.before_wrapped_validate(environment)
        return self.__wrapped.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.before_wrapped_prepare(environment, script_output_dir_path)
        return self.__wrapped.prepare(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.before_wrapped_execute(environment, script_output_dir_path, std_files)
        return self.__wrapped.execute(environment, script_output_dir_path, std_files)


class ActSourceAndExecutorConstructorForConstantExecutor(ActSourceAndExecutorConstructor):
    def __init__(self, executor: ActSourceAndExecutor):
        self.executor = executor

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        return self.executor


class ActSourceAndExecutorConstructorWithActionsForExecutor(ActSourceAndExecutorConstructor):
    def __init__(self,
                 wrapped: ActSourceAndExecutorConstructor,
                 before_wrapped_validate_pre_sds=do_nothing,
                 before_wrapped_validate_post_setup=do_nothing,
                 before_wrapped_prepare=do_nothing,
                 before_wrapped_execute=do_nothing):
        self.__wrapped = wrapped
        self.before_wrapped_validate = before_wrapped_validate_post_setup
        self.before_wrapped_validate_pre_sds = before_wrapped_validate_pre_sds
        self.before_wrapped_prepare = before_wrapped_prepare
        self.before_wrapped_execute = before_wrapped_execute

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        wrapped_executor = self.__wrapped.apply(os_process_executor, environment, act_phase_instructions)
        return ActSourceAndExecutorWrapperWithActions(
            wrapped_executor,
            before_wrapped_validate=self.before_wrapped_validate,
            before_wrapped_prepare=self.before_wrapped_prepare,
            before_wrapped_execute=self.before_wrapped_execute,
            before_wrapped_validate_pre_sds=self.before_wrapped_validate_pre_sds)
