from abc import ABC, abstractmethod

from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class CommandExecutor(ABC):
    """Executes a :class:`Command` (as a sub process)"""

    @abstractmethod
    def execute(self,
                command: Command,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        """
        :raises :class:`HardErrorException`: Unable to execute.
        :return: Exit code from execution.
        """
