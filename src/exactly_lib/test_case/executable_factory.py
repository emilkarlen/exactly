from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import Executable


class ExecutableFactory:
    def make(self, command: Command) -> Executable:
        raise NotImplementedError('abstract method')
