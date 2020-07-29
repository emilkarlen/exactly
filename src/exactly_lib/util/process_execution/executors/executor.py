from abc import ABC

from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case_utils.program_execution.command_processor import CommandProcessor
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class ProcessorFromExecutor(CommandProcessor[int], ABC):
    """Executes a :class:`Command` via a :class:`CommandExecutor`"""

    def __init__(self,
                 executor: CommandExecutor,
                 files: StdFiles,
                 ):
        self._executor = executor
        self._files = files

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> int:
        """
        :raises :class:`HardErrorException`: Unable to execute :class:`Command`
        :return: Exit code
        """
        return self._executor.execute(
            command,
            settings,
            self._files,
        )
