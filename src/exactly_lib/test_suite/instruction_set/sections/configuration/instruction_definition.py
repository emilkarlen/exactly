from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.test_suite.instruction_set.instruction import TestSuiteInstruction


class ConfigurationSectionEnvironment:
    def __init__(self,
                 initial_preprocessor: Preprocessor,
                 initial_act_phase_setup: ActPhaseSetup):
        self._preprocessor = initial_preprocessor
        self._act_phase_setup = initial_act_phase_setup

    @property
    def preprocessor(self) -> Preprocessor:
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, value: Preprocessor):
        self._preprocessor = value

    @property
    def act_phase_setup(self) -> ActPhaseSetup:
        return self._act_phase_setup

    @act_phase_setup.setter
    def act_phase_setup(self, value: ActPhaseSetup):
        self._act_phase_setup = value


class ConfigurationSectionInstruction(TestSuiteInstruction):
    def execute(self, environment: ConfigurationSectionEnvironment):
        """
        Updates the environment.
        """
        raise NotImplementedError()
