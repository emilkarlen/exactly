from abc import ABC, abstractmethod
from typing import TypeVar, Generic, ContextManager

from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.process_execution.process_executor import ProcessExecutionFile

MODEL = TypeVar('MODEL')


class RunConfiguration(Generic[MODEL], ABC):
    @abstractmethod
    def stdin(self, model: MODEL) -> ContextManager[ProcessExecutionFile]:
        pass

    @abstractmethod
    def program_for_model(self,
                          matcher_argument_program: Program,
                          model: MODEL,
                          ) -> Program:
        """Gives the program to run on the given model.

        :param matcher_argument_program: The program given as argument to the "run" matcher.
        """
        pass
