from enum import Enum

from exactly_lib.execution.partial_execution import TestCase
from exactly_lib.section_document import model


class PartialPhase(Enum):
    SETUP = 1
    ACT = 2
    BEFORE_ASSERT = 3
    ASSERT = 4
    CLEANUP = 5


class TestCaseGeneratorForPartialExecutionBase:
    """
    Base class for generation of Test Cases for full execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    def phase_contents_for(self, phase: PartialPhase) -> model.SectionContents:
        raise NotImplementedError()

    @property
    def test_case(self) -> TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> TestCase:
        return TestCase(
                self.phase_contents_for(PartialPhase.SETUP),
                self.phase_contents_for(PartialPhase.ACT),
                self.phase_contents_for(PartialPhase.BEFORE_ASSERT),
                self.phase_contents_for(PartialPhase.ASSERT),
                self.phase_contents_for(PartialPhase.CLEANUP)
        )
