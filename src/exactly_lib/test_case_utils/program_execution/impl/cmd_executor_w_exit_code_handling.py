from pathlib import Path
from typing import Generic, Callable

from exactly_lib.test_case_utils.program import top_lvl_error_msg_rendering
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.file_utils.text_reader import TextFromFileReader
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_executor import T


class Executor(Generic[T], CommandExecutor[T]):
    def __init__(self,
                 err_msg_reader: TextFromFileReader,
                 get_exit_code: Callable[[T], int],
                 get_stderr: Callable[[T], Path],
                 handled: CommandExecutor[T],
                 ):
        self.err_msg_reader = err_msg_reader
        self.get_stderr = get_stderr
        self.get_exit_code = get_exit_code
        self.handled = handled

    def execute(self,
                settings: ProcessExecutionSettings,
                command: Command,
                program_for_err_msg: StructureRenderer,
                ) -> T:
        result = self.handled.execute(settings, command, program_for_err_msg)
        self._handle_result(result, program_for_err_msg)
        return result

    def _handle_result(self,
                       result: T,
                       program_for_err_msg: StructureRenderer):
        exit_code = self.get_exit_code(result)

        if exit_code == 0:
            return

        raise HardErrorException(
            top_lvl_error_msg_rendering.non_zero_exit_code_msg(
                program_for_err_msg,
                exit_code,
                self._stderr_part(result),
            )
        )

    def _stderr_part(self, result: T) -> str:
        with self.get_stderr(result).open() as f:
            return self.err_msg_reader.read(f)
