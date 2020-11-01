from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings

RET = TypeVar('RET')


class CommandProcessor(Generic[RET], ABC):
    """Executes a :class:`Command`, with custom std-files and custom processing of the result."""

    @abstractmethod
    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> RET:
        """
        :raises :class:`HardErrorException`: Unable to execute :class:`Command`
        """
