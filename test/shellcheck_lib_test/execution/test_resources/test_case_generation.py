import shellcheck_lib_test.test_resources.model_utils
from shellcheck_lib.document import model
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case.sections.common import TestCaseInstruction


class LinesGenerator:
    def __init__(self):
        self.__previous_line_number = 0

    def next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    __next__ = next_line


class InstructionLineConstructor:
    def __init__(self,
                 lines_generator: LinesGenerator):
        self.lines_generator = lines_generator

    def apply(self, instruction: TestCaseInstruction) -> model.PhaseContentElement:
        return shellcheck_lib_test.test_resources.model_utils.new_instruction_element(
                self.lines_generator.next_line(),
                instruction)

    __call__ = apply

    def apply_list(self, instructions: iter) -> list:
        return [self.apply(instruction) for instruction in instructions]


def instruction_line_constructor() -> InstructionLineConstructor:
    return InstructionLineConstructor(LinesGenerator())


def phase_contents(phase_content_elements: list) -> model.PhaseContents:
    return model.PhaseContents(tuple(phase_content_elements))


class TestCaseGeneratorBase:
    def setup_phase(self) -> model.PhaseContents:
        return phase_contents(self._setup_phase())

    def act_phase(self) -> model.PhaseContents:
        return phase_contents(self._act_phase())

    def before_assert_phase(self) -> model.PhaseContents:
        return phase_contents(self._before_assert_phase())

    def assert_phase(self) -> model.PhaseContents:
        return phase_contents(self._assert_phase())

    def cleanup_phase(self) -> model.PhaseContents:
        return phase_contents(self._cleanup_phase())

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

    def _before_assert_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type BeforeAssertPhaseInstruction)
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


class TestCaseInstructionsForPartialExecution(tuple):
    def __new__(cls):
        return tuple.__new__(cls, ([], [], [], []))

    @property
    def setup_instructions(self) -> list:
        return self[0]

    @property
    def act_instructions(self) -> list:
        return self[1]

    @property
    def assert_instructions(self) -> list:
        return self[2]

    @property
    def cleanup_instructions(self) -> list:
        return self[3]


class TestCaseInstructionsForFullExecution(tuple):
    def __new__(cls):
        return tuple.__new__(cls, ([], [], [], [], []))

    @property
    def config_instructions(self) -> list:
        return self[0]

    @property
    def setup_instructions(self) -> list:
        return self[1]

    @property
    def act_instructions(self) -> list:
        return self[2]

    @property
    def assert_instructions(self) -> list:
        return self[3]

    @property
    def cleanup_instructions(self) -> list:
        return self[4]
