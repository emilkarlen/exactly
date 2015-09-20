from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.test_case_processing import Preprocessor


class AnonymousSectionEnvironment:
    def __init__(self):
        self._preprocessor = 1

    @property
    def preprocessor(self) -> Preprocessor:
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, value: Preprocessor):
        self._preprocessor = value


class AnonymousSectionInstruction(Instruction):
    def execute(self,
                environment: AnonymousSectionEnvironment):
        """
        Updates the environment.
        """
        raise NotImplementedError()
