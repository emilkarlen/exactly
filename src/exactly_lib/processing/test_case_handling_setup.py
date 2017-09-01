from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.test_case_processing import Preprocessor


class TestCaseHandlingSetup(tuple):
    def __new__(cls,
                act_phase_setup: ActPhaseSetup,
                preprocessor: Preprocessor):
        return tuple.__new__(cls, (act_phase_setup, preprocessor))

    @property
    def act_phase_setup(self) -> ActPhaseSetup:
        return self[0]

    @property
    def preprocessor(self) -> Preprocessor:
        return self[1]
