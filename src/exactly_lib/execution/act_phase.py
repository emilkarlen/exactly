import pathlib

from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.execution.result import FailureDetails
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
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


class SourceSetup:
    def __init__(self,
                 script_builder: ActSourceBuilder,
                 script_output_dir_path: pathlib.Path):
        self.script_builder = script_builder
        self.script_output_dir_path = script_output_dir_path


class ActSourceExecutor:
    def validate(self,
                 home_dir: pathlib.Path,
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        """
        Validates the given source.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        """
        Executed after validate.

        An opportunity to prepare for execution.

        E.g. write the source code to file.
        """
        raise NotImplementedError()

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        """
        Executed after prepare.

        :returns exit code of executed program, or error
        """
        raise NotImplementedError()
