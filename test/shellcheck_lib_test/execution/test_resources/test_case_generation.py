import shellcheck_lib_test.test_resources.model_utils
from shellcheck_lib.document import model
from shellcheck_lib.general import line_source


class TestCaseGeneratorBase:
    """
    Base class for generation of Test Cases using dummy source lines.

    Generates and stores a single test case.

    The test case is build/generated only a single time.
    """

    def __init__(self):
        self.__previous_line_number = 0

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
        return shellcheck_lib_test.test_resources.model_utils.new_instruction_element(
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
