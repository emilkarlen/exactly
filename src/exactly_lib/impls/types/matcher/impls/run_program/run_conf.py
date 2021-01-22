from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.string_source import StringSource

MODEL = TypeVar('MODEL')


class RunConfiguration(Generic[MODEL], ABC):
    @abstractmethod
    def additional_stdin(self, model: MODEL) -> List[StringSource]:
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
