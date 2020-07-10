from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.test_case_utils.program.execution.exe_wo_transformation import ExecutionResultAndStderr
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.program.program import Program

MODEL = TypeVar('MODEL')


class Runner(Generic[MODEL], ABC):
    def __init__(self, application_environment: ApplicationEnvironment):
        self._application_environment = application_environment

    @abstractmethod
    def run(self,
            program_for_model: Program,
            model: MODEL,
            ) -> ExecutionResultAndStderr:
        """
        :param program_for_model: The program given by `program_for_model`
        """
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
