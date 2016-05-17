from exactly_lib.execution import phases
from exactly_lib.section_document import model
from exactly_lib.test_case import test_case_doc


class TestCaseGeneratorForFullExecutionBase:
    """
    Base class for generation of Test Cases for full execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    def phase_contents_for(self, phase: phases.Phase) -> model.SectionContents:
        raise NotImplementedError()

    @property
    def test_case(self) -> test_case_doc.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> test_case_doc.TestCase:
        return test_case_doc.TestCase(
                self.phase_contents_for(phases.CONFIGURATION),
                self.phase_contents_for(phases.SETUP),
                self.phase_contents_for(phases.ACT),
                self.phase_contents_for(phases.BEFORE_ASSERT),
                self.phase_contents_for(phases.ASSERT),
                self.phase_contents_for(phases.CLEANUP)
        )
