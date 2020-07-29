from abc import ABC, abstractmethod
from typing import Generic

from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_executor import T


class CommandProcessor(Generic[T], ABC):
    """Executes a :class:`Command`, with custom std-files and custom processing of the result."""

    @abstractmethod
    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> T:
        """
        :raises :class:`HardErrorException`: Unable to execute :class:`Command`
        """
