from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.std import StdFiles


class ActPhaseOsProcessExecutorThatRecordsArguments(ActPhaseOsProcessExecutor):
    def __init__(self):
        self.command = None
        self.process_execution_settings = None

    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        self.command = command
        self.process_execution_settings = process_execution_settings
        return new_eh_exit_code(0)
