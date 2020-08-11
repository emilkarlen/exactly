from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class CommandExecutorThatRecordsArguments(CommandExecutor):
    def __init__(self):
        self.command = None
        self.process_execution_settings = None

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        self.command = command
        self.process_execution_settings = settings
        return 0


class CommandExecutorThatJustReturnsConstant(CommandExecutor):
    def __init__(self, constant_return_value: int = 0):
        self.constant_return_value = constant_return_value

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        return self.constant_return_value


class CommandExecutorThatRaisesHardError(CommandExecutor):
    def __init__(self, err_msg: TextRenderer):
        self.err_msg = err_msg

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        raise HardErrorException(self.err_msg)