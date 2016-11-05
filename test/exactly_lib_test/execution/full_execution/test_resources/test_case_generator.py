from exactly_lib.section_document import model
from exactly_lib.test_case import test_case_doc, phase_identifier


class TestCaseGeneratorForFullExecutionBase:
    """
    Base class for generation of Test Cases for full execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    def phase_contents_for(self, phase: phase_identifier.Phase) -> model.SectionContents:
        raise NotImplementedError()

    @property
    def test_case(self) -> test_case_doc.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> test_case_doc.TestCase:
        return test_case_doc.TestCase(
            self.phase_contents_for(phase_identifier.CONFIGURATION),
            self.phase_contents_for(phase_identifier.SETUP),
            self.phase_contents_for(phase_identifier.ACT),
            self.phase_contents_for(phase_identifier.BEFORE_ASSERT),
            self.phase_contents_for(phase_identifier.ASSERT),
            self.phase_contents_for(phase_identifier.CLEANUP)
        )
