import unittest
from typing import Optional, Any, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.std import StdFiles, ProcessExecutionFile
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.test_resources.recording import MaxNumberOfTimesChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class CommandExecutorWInitialAction(CommandExecutor):
    def __init__(self,
                 delegated: CommandExecutor,
                 initial_action: Callable[[Command, ProcessExecutionSettings], Any],
                 ):
        self._initial_action = initial_action
        self._delegated = delegated

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        self._initial_action(command, settings)
        return self._delegated.execute(command, settings, files)


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


class CommandExecutorWithMaxNumInvocations(CommandExecutor):
    def __init__(self,
                 put: unittest.TestCase,
                 max_num_invocations: int,
                 delegated: CommandExecutor,
                 err_msg_header: str = '',
                 ):
        self._put = put
        self._delegated = delegated

        self._invocations_checker = MaxNumberOfTimesChecker(
            put,
            max_num_invocations,
            'applications of CommandExecutor',
            err_msg_header,
        )

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        self._invocations_checker.register()
        return self._delegated.execute(command, settings, files)


class CommandExecutorThatJustReturnsConstant(CommandExecutor):
    def __init__(self,
                 constant_return_value: int = 0,
                 string_to_write_to_stderr: Optional[str] = None):
        self.constant_return_value = constant_return_value
        self.string_to_write_to_stderr = string_to_write_to_stderr

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        if self.string_to_write_to_stderr is not None:
            files.output.err.write(self.string_to_write_to_stderr)

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


class CommandExecutorThatChecksStdin(CommandExecutor):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: Assertion[ProcessExecutionFile],
                 exit_code: int = 0,
                 ):
        self._put = put
        self._expectation = expectation
        self.exit_code = exit_code

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        self._expectation.apply_with_message(self._put,
                                             files.stdin,
                                             'stdin given to command executor')
        return self.exit_code
