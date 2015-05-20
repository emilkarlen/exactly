from shelltest.document import model
from shelltest.document import line_source
from shelltest.test_case import abs_syn_gen


class TestCaseGeneratorBase:
    """
    Base class for generation of Test Cases using dummy source lines.

    Generates and stores a single test case.

    The test case is build/generated only a single time.
    """

    def __init__(self):
        self.__previous_line_number = 0
        self.__test_case = None

    @property
    def test_case(self) -> abs_syn_gen.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> abs_syn_gen.TestCase:
        return abs_syn_gen.TestCase(
            self.__from(self._anonymous_phase()),
            self.__from(self._setup_phase()),
            self.__from(self._act_phase()),
            self.__from(self._assert_phase()),
            self.__from(self._cleanup_phase())
        )

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
        return model.new_instruction_element(
            self._next_line(),
            instruction)

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    def _anonymous_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AnonymousPhaseInstruction)
        """
        return []

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
    def __from(phase_content_elements: list) -> model.PhaseContents:
        return model.PhaseContents(tuple(phase_content_elements))

