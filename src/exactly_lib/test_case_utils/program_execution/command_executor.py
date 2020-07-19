from abc import ABC, abstractmethod
from typing import Generic

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_executor import T


class CommandExecutor(Generic[T], ABC):
    """Executes a Command"""

    @abstractmethod
    def execute(self,
                settings: ProcessExecutionSettings,
                command: Command,
                program_for_err_msg: StructureRenderer,
                ) -> T:
        pass
