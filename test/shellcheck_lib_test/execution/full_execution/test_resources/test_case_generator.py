from shellcheck_lib.document import model
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib_test.execution.test_resources.test_case_generation import TestCaseGeneratorBase, phase_contents


class TestCaseGeneratorForFullExecutionBase(TestCaseGeneratorBase):
    """
    Base class for generation of Test Cases for full execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    def anonymous_phase(self) -> model.PhaseContents:
        return phase_contents(self._anonymous_phase())

    def _anonymous_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AnonymousPhaseInstruction)
        """
        return []

    @property
    def test_case(self) -> test_case_doc.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> test_case_doc.TestCase:
        return test_case_doc.TestCase(
                self.anonymous_phase(),
                self.setup_phase(),
                self.act_phase(),
                self.assert_phase(),
                self.cleanup_phase()
        )
