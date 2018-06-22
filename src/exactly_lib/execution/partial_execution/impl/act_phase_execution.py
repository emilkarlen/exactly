import pathlib
import subprocess
from contextlib import contextmanager
from typing import Optional, Callable

from exactly_lib.execution.impl.result import PhaseStepFailure, ActionWithFailureAsResult
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import StdinConfiguration
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_hard_error
from exactly_lib.test_case_file_structure.sandbox_directory_structure import stdin_contents_file
from exactly_lib.util.failure_details import FailureDetails, new_failure_details_from_exception, \
    new_failure_details_from_message
from exactly_lib.util.file_utils import open_and_make_read_only_on_close, write_new_text_file
from exactly_lib.util.std import StdFiles, StdOutputFiles

PhaseStepFailureConstructorType = Callable[[PartialExeResultStatus, FailureDetails], PhaseStepFailure]


class ActPhaseExecutor:
    """
    Methods that corresponds to each step of the execution of the ATC.

    These methods must be invoked in the correct order (as defined by partial execution).

    A single object must be used for a single execution.

    Creates the ACT outcome files (under result/)

    Stores parts of the ACT outcome as an object in the instance.
    """

    def __init__(self,
                 act_source_and_executor: ActSourceAndExecutor,
                 environment_for_validate_post_setup: InstructionEnvironmentForPostSdsStep,
                 environment_for_other_steps: InstructionEnvironmentForPostSdsStep,
                 stdin_configuration: StdinConfiguration,
                 exe_atc_and_skip_assertions: Optional[StdOutputFiles]):
        self.act_source_and_executor = act_source_and_executor
        self.environment_for_validate_post_setup = environment_for_validate_post_setup
        self.environment_for_other_steps = environment_for_other_steps
        self.home_and_sds = environment_for_other_steps.home_and_sds
        self.stdin_configuration = stdin_configuration
        self.script_output_dir_path = environment_for_other_steps.home_and_sds.sds.test_case_dir
        self.exe_atc_and_skip_assertions = exe_atc_and_skip_assertions

        self._action_to_check_outcome = None

    @property
    def action_to_check_outcome(self) -> Optional[ActionToCheckOutcome]:
        """
        :return: Not None iff all steps have executed successfully.
        """
        return self._action_to_check_outcome

    def validate_post_setup(self, failure_con: PhaseStepFailureConstructorType) -> ActionWithFailureAsResult:
        def action() -> Optional[PhaseStepFailure]:
            res = self.act_source_and_executor.validate_post_setup(self.environment_for_validate_post_setup)
            if res.is_success:
                return None
            else:
                return failure_con(PartialExeResultStatus(res.status.value),
                                   new_failure_details_from_message(res.failure_message))

        return action

    def prepare(self, failure_con: PhaseStepFailureConstructorType) -> ActionWithFailureAsResult:
        def action() -> Optional[PhaseStepFailure]:
            res = self.act_source_and_executor.prepare(self.environment_for_other_steps,
                                                       self.script_output_dir_path)
            if res.is_success:
                return None
            else:
                return failure_con(PartialExeResultStatus.HARD_ERROR,
                                   new_failure_details_from_message(res.failure_message))

        return action

    def execute(self, failure_con: PhaseStepFailureConstructorType) -> ActionWithFailureAsResult:
        def action() -> Optional[PhaseStepFailure]:
            exit_code_or_hard_error = self._execute_with_stdin_handling()
            if exit_code_or_hard_error.is_exit_code:
                return None
            else:
                return failure_con(PartialExeResultStatus.HARD_ERROR,
                                   exit_code_or_hard_error.failure_details)

        return action

    def _execute_with_stdin_handling(self) -> ExitCodeOrHardError:
        if self.stdin_configuration.has_custom_stdin:
            file_name = self._custom_stdin_file_name()
            return self._run_act_program_with_opened_stdin_file(file_name)
        else:
            return self._run_act_program_with_stdin_file(subprocess.DEVNULL)

    def _run_act_program_with_opened_stdin_file(self, file_name: pathlib.Path) -> ExitCodeOrHardError:
        try:
            with file_name.open() as f_stdin:
                return self._run_act_program_with_stdin_file(f_stdin)
        except IOError as ex:
            return new_eh_hard_error(new_failure_details_from_exception(
                ex,
                'Failure to open stdin file: ' + str(file_name)))

    def _run_act_program_with_stdin_file(self, f_stdin) -> ExitCodeOrHardError:
        with self._std_output_files() as std_output_files:
            std_files = StdFiles(f_stdin, std_output_files)
            return self._run_act_program_with_std_files(std_files)

    def _run_act_program_with_std_files(self,
                                        std_files: StdFiles) -> ExitCodeOrHardError:
        exit_code_or_hard_error = self.act_source_and_executor.execute(
            self.environment_for_other_steps,
            self.script_output_dir_path,
            std_files)
        self._register_outcome(exit_code_or_hard_error)
        return exit_code_or_hard_error

    @contextmanager
    def _std_output_files(self):
        if self.exe_atc_and_skip_assertions is not None:
            yield self.exe_atc_and_skip_assertions
        else:
            sds = self.home_and_sds.sds
            with open_and_make_read_only_on_close(str(sds.result.stdout_file), 'w') as f_stdout:
                with open_and_make_read_only_on_close(str(sds.result.stderr_file), 'w') as f_stderr:
                    yield StdOutputFiles(f_stdout, f_stderr)

    def _register_outcome(self, exit_code_or_hard_error: ExitCodeOrHardError):
        if exit_code_or_hard_error.is_exit_code:
            self._action_to_check_outcome = ActionToCheckOutcome(exit_code_or_hard_error.exit_code)
            if self.exe_atc_and_skip_assertions is None:
                self._store_exit_code(exit_code_or_hard_error.exit_code)

    def _store_exit_code(self, exitcode: int):
        with open_and_make_read_only_on_close(str(self.home_and_sds.sds.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def _custom_stdin_file_name(self) -> pathlib.Path:
        configuration = self.stdin_configuration
        if configuration.file_name is not None:
            return configuration.file_name
        else:
            file_path = stdin_contents_file(self.home_and_sds.sds)
            write_new_text_file(file_path, configuration.string_contents)
            return file_path
