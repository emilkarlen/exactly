import shellcheck_lib_test.util.model_utils
from shellcheck_lib.document import model
from shellcheck_lib.execution import partial_execution
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import test_case_doc


class TestCaseGeneratorBase:
    """
    Base class for generation of Test Cases using dummy source lines.

    Generates and stores a single test case.

    The test case is build/generated only a single time.
    """

    def __init__(self):
        self.__previous_line_number = 0

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
        return shellcheck_lib_test.util.model_utils.new_instruction_element(
                self._next_line(),
                instruction)

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    def _setup_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return []

    def _act_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return []

    def _assert_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return []

    def _cleanup_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return []

    @staticmethod
    def _from(phase_content_elements: list) -> model.PhaseContents:
        return model.PhaseContents(tuple(phase_content_elements))


class TestCaseGeneratorForPartialExecutionBase(TestCaseGeneratorBase):
    """
    Base class for generation of Test Cases for partial execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    @property
    def test_case(self) -> partial_execution.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> partial_execution.TestCase:
        return partial_execution.TestCase(
                self._from(self._setup_phase()),
                self._from(self._act_phase()),
                self._from(self._assert_phase()),
                self._from(self._cleanup_phase())
        )


class TestCaseGeneratorForFullExecutionBase(TestCaseGeneratorBase):
    """
    Base class for generation of Test Cases for full execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    @property
    def test_case(self) -> test_case_doc.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> test_case_doc.TestCase:
        return test_case_doc.TestCase(
                self._from(self._anonymous_phase()),
                self._from(self._setup_phase()),
                self._from(self._act_phase()),
                self._from(self._assert_phase()),
                self._from(self._cleanup_phase())
        )

    def _anonymous_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AnonymousPhaseInstruction)
        """
        return []
