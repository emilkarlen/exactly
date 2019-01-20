import pathlib
from typing import Sequence

from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.std import StdFiles


class AtcOsProcessExecutor:
    """
    Executes a command in a sub process
    """

    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        raise NotImplementedError()


class ParseException(Exception):
    def __init__(self, cause: svh.SuccessOrValidationErrorOrHardError):
        self.cause = cause
        if cause.is_success:
            raise ValueError('A {} cannot represent SUCCESS'.format(str(type(self))))


class ActionToCheck(SymbolUser):
    """
    Executes the ATC.
    """

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        pre-sds validation of the source that this object represents.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        """
        post-setup validation of the source that this object represents.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        """
        Executed after validate.

        An opportunity to prepare for execution.

        E.g. write the source code to file.
        """
        raise NotImplementedError()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        """
        Executed after prepare.

        :returns exit code of executed program, or error
        """
        raise NotImplementedError()


class Actor:
    """
    Parses the contents of the act phase which is the source that is to be executed as the act phase.
    (after it has been extracted from the test case file).

    Does syntax checking/validation while parsing - and reports syntax errors
    in terms of exceptions.
    """

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        """
        :raises ParseException
        """
        raise NotImplementedError()
