from pathlib import Path
from typing import Generic, Callable

from exactly_lib.impls.program_execution.command_processor import CommandProcessor, RET
from exactly_lib.impls.types.program import top_lvl_error_msg_rendering
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.text_reader import TextFromFileReader
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class Processor(Generic[RET], CommandProcessor[RET]):
    def __init__(self,
                 err_msg_reader: TextFromFileReader,
                 get_exit_code: Callable[[RET], int],
                 get_stderr: Callable[[RET], Path],
                 handled: CommandProcessor[RET],
                 ):
        self.err_msg_reader = err_msg_reader
        self.get_stderr = get_stderr
        self.get_exit_code = get_exit_code
        self.handled = handled

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> RET:
        result = self.handled.process(settings, command)
        self._handle_result(result, command)
        return result

    def _handle_result(self,
                       result: RET,
                       command: Command,
                       ):
        exit_code = self.get_exit_code(result)

        if exit_code == 0:
            return

        raise HardErrorException(
            top_lvl_error_msg_rendering.non_zero_exit_code_msg(
                command.new_structure_builder().build(),
                exit_code,
                self._stderr_part(result),
            )
        )

    def _stderr_part(self, result: RET) -> str:
        with self.get_stderr(result).open() as f:
            return self.err_msg_reader.read(f)
