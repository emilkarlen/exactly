from contextlib import contextmanager
from typing import Optional, Callable, ContextManager

from exactly_lib.execution.impl.result import ActionThatRaisesPhaseStepFailureException
from exactly_lib.execution.result import ActionToCheckOutcome, ExecutionFailureStatus, PhaseStepFailure, \
    PhaseStepFailureException
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import ActionToCheck
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.file_utils import misc_utils
from exactly_lib.util.file_utils.std import StdOutputFiles

PhaseStepFailureConstructorType = Callable[[ExecutionFailureStatus, FailureDetails], PhaseStepFailure]


class ActionToCheckExecutor:
    """
    Methods that corresponds to each step of the execution of the ATC.

    These methods must be invoked in the correct order (as defined by partial execution).

    A single object must be used for a single execution.

    Creates the ACT outcome files (under result/)

    Stores parts of the ACT outcome as an object in the instance.
    """

    def __init__(self,
                 atc: ActionToCheck,
                 environment_for_validate_post_setup: InstructionEnvironmentForPostSdsStep,
                 environment_for_other_steps: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices,
                 atc_input: AdvWValidation[AtcExecutionInput],
                 exe_atc_and_skip_assertions: Optional[StdOutputFiles]):
        self.atc = atc
        self.environment_for_validate_post_setup = environment_for_validate_post_setup
        self.environment_for_other_steps = environment_for_other_steps
        self.os_services = os_services
        self.tcds = environment_for_other_steps.tcds
        self.atc_input = atc_input
        self.exe_atc_and_skip_assertions = exe_atc_and_skip_assertions

        self._atc_outcome = None

    @property
    def action_to_check_outcome(self) -> Optional[ActionToCheckOutcome]:
        """
        :return: Not None iff all steps have executed successfully.
        """
        return self._atc_outcome

    def validate_execution_info(self,
                                failure_con: PhaseStepFailureConstructorType,
                                ) -> ActionThatRaisesPhaseStepFailureException:
        def action():
            mb_failure_message = self.atc_input.validate()
            if mb_failure_message:
                raise PhaseStepFailureException(
                    failure_con(ExecutionFailureStatus.HARD_ERROR,
                                FailureDetails.new_message(mb_failure_message))
                )

        return action

    def validate_post_setup(self,
                            failure_con: PhaseStepFailureConstructorType) -> ActionThatRaisesPhaseStepFailureException:
        def action():
            res = self.atc.validate_post_setup(self.environment_for_validate_post_setup)
            if not res.is_success:
                raise PhaseStepFailureException(
                    failure_con(ExecutionFailureStatus(res.status.value),
                                FailureDetails.new_message(res.failure_message))
                )

        return action

    def prepare(self, failure_con: PhaseStepFailureConstructorType) -> ActionThatRaisesPhaseStepFailureException:
        def action():
            res = self.atc.prepare(self.environment_for_other_steps,
                                   self.os_services)
            if not res.is_success:
                raise PhaseStepFailureException(
                    failure_con(ExecutionFailureStatus.HARD_ERROR,
                                FailureDetails.new_message(res.failure_message))
                )

        return action

    def execute(self, failure_con: PhaseStepFailureConstructorType) -> ActionThatRaisesPhaseStepFailureException:
        def action():
            exit_code_or_hard_error = self._do_execute()
            if not exit_code_or_hard_error.is_exit_code:
                raise PhaseStepFailureException(
                    failure_con(ExecutionFailureStatus.HARD_ERROR,
                                exit_code_or_hard_error.failure_details)
                )

        return action

    def _do_execute(self) -> ExitCodeOrHardError:
        with self._std_output_files() as std_output_files:
            return self._do_execute_w_output_files(std_output_files)

    def _do_execute_w_output_files(self, output: StdOutputFiles) -> ExitCodeOrHardError:
        exit_code_or_hard_error = self.atc.execute(
            self.environment_for_other_steps,
            self.os_services,
            self.atc_input.resolve(self._app_env_for_execute()),
            output,
        )
        self._register_outcome(exit_code_or_hard_error)
        return exit_code_or_hard_error

    @contextmanager
    def _std_output_files(self) -> ContextManager[StdOutputFiles]:
        if self.exe_atc_and_skip_assertions is not None:
            yield self.exe_atc_and_skip_assertions
        else:
            sds = self.tcds.sds
            with misc_utils.open_and_make_read_only_on_close__text(sds.result.stdout_file, 'w') as f_stdout:
                with misc_utils.open_and_make_read_only_on_close__text(sds.result.stderr_file, 'w') as f_stderr:
                    yield StdOutputFiles(f_stdout, f_stderr)

    def _register_outcome(self, exit_code_or_hard_error: ExitCodeOrHardError):
        if exit_code_or_hard_error.is_exit_code:
            self._atc_outcome = ActionToCheckOutcome(exit_code_or_hard_error.exit_code)
            if self.exe_atc_and_skip_assertions is None:
                self._store_exit_code(exit_code_or_hard_error.exit_code)

    def _store_exit_code(self, exitcode: int):
        with misc_utils.open_and_make_read_only_on_close__text(self.tcds.sds.result.exitcode_file, 'w') as f:
            f.write(str(exitcode))

    def _app_env_for_execute(self) -> ApplicationEnvironment:
        env = self.environment_for_other_steps
        return ApplicationEnvironment(
            self.os_services,
            env.proc_exe_settings,
            env.tmp_dir__path_access.paths_access,
            env.mem_buff_size,
        )
