import pathlib

from exactly_lib.execution.act_phase import ActSourceAndExecutor, ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


class ActSourceAndExecutorWithConstantExecutionResult(ActSourceAndExecutor):
    def __init__(self,
                 execution_result: ExitCodeOrHardError = new_eh_exit_code(0)):
        self.execution_result = execution_result

    def validate_post_setup(self, home_and_sds: HomeAndSds) -> svh.SuccessOrValidationErrorOrHardError:
        pass

    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        pass

    def prepare(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        pass

    def execute(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return
