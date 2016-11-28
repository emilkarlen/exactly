import pathlib

from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.process_execution.os_process_execution import Command, ProcessExecutionSettings
from exactly_lib.util.std import StdFiles


class ExitCodeOrHardError(tuple):
    """
    Represents EITHER success(with exit code) OR hard error.
    """

    def __new__(cls,
                exit_code: int,
                failure_message: FailureDetails):
        return tuple.__new__(cls, (exit_code, failure_message))

    @property
    def is_exit_code(self) -> bool:
        return self[0] is not None

    @property
    def is_hard_error(self) -> bool:
        return self[0] is None

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def failure_details(self) -> FailureDetails:
        """
        :return None iff the object represents SUCCESS.
        """
        return self[1]

    @property
    def is_hard_error(self) -> bool:
        return not self.is_exit_code

    def __str__(self):
        if self.is_exit_code:
            return 'SUCCESS'
        else:
            return 'FAILURE:{}'.format(str(self.failure_details))


def new_eh_exit_code(exit_code: int) -> ExitCodeOrHardError:
    return ExitCodeOrHardError(exit_code, None)


def new_eh_hard_error(failure_details: FailureDetails) -> ExitCodeOrHardError:
    if failure_details is None:
        raise ValueError('A HARD ERROR must have failure details (that is not None)')
    return ExitCodeOrHardError(None, failure_details)


class ActSourceAndExecutor:
    """
    Valid act phase source together with functionality for executing it.
    """

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        pre-sds validation of the source that this object represents.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        post-setup validation of the source that this object represents.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        """
        Executed after validate.

        An opportunity to prepare for execution.

        E.g. write the source code to file.
        """
        raise NotImplementedError()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        """
        Executed after prepare.

        :returns exit code of executed program, or error
        """
        raise NotImplementedError()


class ActPhaseOsProcessExecutor:
    """
    Executes a command in a sub process
    """

    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        raise NotImplementedError()


class ActSourceAndExecutorConstructor:
    """
    Parses the contents of the act phase which is the source that is to be executed as the act phase.
    (after it has been extracted from the test case file).

    Does syntax checking/validation while parsing - and reports syntax errors
    in terms of exceptions.
    """

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        raise NotImplementedError()


class ActPhaseHandling:
    def __init__(self, source_and_executor_constructor: ActSourceAndExecutorConstructor):
        self.source_and_executor_constructor = source_and_executor_constructor
