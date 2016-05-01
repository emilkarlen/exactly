from exactly_lib.test_case.test_case_processing import Preprocessor
from exactly_lib.test_suite.instruction_set.instruction import TestSuiteInstruction


class ConfigurationSectionEnvironment:
    def __init__(self,
                 initial_preprocessor: Preprocessor):
        self._preprocessor = initial_preprocessor

    @property
    def preprocessor(self) -> Preprocessor:
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, value: Preprocessor):
        self._preprocessor = value


class ConfigurationSectionInstruction(TestSuiteInstruction):
    def execute(self,
                environment: ConfigurationSectionEnvironment):
        """
        Updates the environment.
        """
        raise NotImplementedError()
