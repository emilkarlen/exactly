from exactly_lib.impls.program_execution.executable_factory import ExecutableFactory
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution import process_executor
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_executor import ProcessExecutor


class CommandExecutorFromProcessExecutor(CommandExecutor):
    """Executes a :class:`Command` via a :class:`ProcessExecutor`"""

    def __init__(self,
                 process_executor: ProcessExecutor,
                 translator: ExecutableFactory,
                 ):
        self._process_executor = process_executor
        self._translator = translator

    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        try:
            return self._process_executor.execute(
                self._translator.make(command),
                settings,
                files,
            )
        except process_executor.ProcessExecutionException as ex:
            _raise_hard_error(command, ex)


def _raise_hard_error(command: Command, ex: process_executor.ProcessExecutionException):
    from exactly_lib.test_case.hard_error import HardErrorException
    from exactly_lib.impls.types.program import top_lvl_error_msg_rendering
    from exactly_lib.util.simple_textstruct.rendering import blocks
    from exactly_lib.util.simple_textstruct.rendering import line_objects
    raise HardErrorException(
        top_lvl_error_msg_rendering.unable_to_execute_program(
            command.new_structure_builder().build(),
            blocks.MajorBlocksOfSingleLineObject(
                line_objects.PreFormattedString.of_str(str(ex.cause))
            )
        )
    )
