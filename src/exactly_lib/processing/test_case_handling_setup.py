from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.test_case_doc import TestCase


class TestCaseTransformer:
    def transform(self, test_case: TestCase) -> TestCase:
        return test_case


class ComposedTestCaseTransformer(TestCaseTransformer):
    def __init__(self,
                 first: TestCaseTransformer,
                 second: TestCaseTransformer):
        self._first = first
        self._second = second

    def transform(self, test_case: TestCase) -> TestCase:
        return self._second.transform(self._first.transform(test_case))


def identity_test_case_transformer() -> TestCaseTransformer:
    return TestCaseTransformer()


class TestCaseHandlingSetup(tuple):
    def __new__(cls,
                act_phase_setup: ActPhaseSetup,
                preprocessor: Preprocessor,
                transformer: TestCaseTransformer = identity_test_case_transformer()):
        return tuple.__new__(cls, (act_phase_setup, preprocessor, transformer))

    @property
    def act_phase_setup(self) -> ActPhaseSetup:
        return self[0]

    @property
    def actor(self) -> Actor:
        return self.act_phase_setup.actor

    @property
    def preprocessor(self) -> Preprocessor:
        return self[1]

    @property
    def transformer(self) -> TestCaseTransformer:
        return self[2]
