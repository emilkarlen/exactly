import exactly_lib_test.section_document.test_resources.elements
from exactly_lib.execution import partial_execution
from exactly_lib.section_document import model
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util import line_source


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

    def apply(self, instruction: TestCaseInstruction) -> model.SectionContentElement:
        return exactly_lib_test.section_document.test_resources.elements.new_instruction_element(
            self.lines_generator.next_line(),
            instruction)

    __call__ = apply

    def apply_list(self, instructions: iter) -> list:
        return [self.apply(instruction) for instruction in instructions]


def partial_test_case_with_instructions(
        setup_phase_instructions: list = (),
        act_phase_instructions: list = (),
        before_assert_phase_instructions: list = (),
        assert_phase_instructions: list = (),
        cleanup_phase_instructions: list = ()) -> partial_execution.TestCase:
    instruction_line_con = instruction_line_constructor()

    def section_contents(instructions: list) -> SectionContents:
        return SectionContents(tuple(map(instruction_line_con, instructions)))

    return partial_execution.TestCase(
        section_contents(setup_phase_instructions),
        section_contents(act_phase_instructions),
        section_contents(before_assert_phase_instructions),
        section_contents(assert_phase_instructions),
        section_contents(cleanup_phase_instructions))


def full_test_case_with_instructions(
        configuration_phase_instructions: list = (),
        setup_phase_instructions: list = (),
        act_phase_instructions: list = (),
        before_assert_phase_instructions: list = (),
        assert_phase_instructions: list = (),
        cleanup_phase_instructions: list = ()) -> test_case_doc.TestCase:
    instruction_line_con = instruction_line_constructor()

    def section_contents(instructions: list) -> SectionContents:
        return SectionContents(tuple(map(instruction_line_con, instructions)))

    return test_case_doc.TestCase(
        section_contents(configuration_phase_instructions),
        section_contents(setup_phase_instructions),
        section_contents(act_phase_instructions),
        section_contents(before_assert_phase_instructions),
        section_contents(assert_phase_instructions),
        section_contents(cleanup_phase_instructions))


def instruction_line_constructor() -> InstructionLineConstructor:
    return InstructionLineConstructor(LinesGenerator())


def phase_contents(phase_content_elements: list) -> model.SectionContents:
    return model.SectionContents(tuple(phase_content_elements))


class TestCaseGeneratorBase:
    def setup_phase(self) -> model.SectionContents:
        return phase_contents(self._setup_phase())

    def act_phase(self) -> model.SectionContents:
        return phase_contents(self._act_phase())

    def before_assert_phase(self) -> model.SectionContents:
        return phase_contents(self._before_assert_phase())

    def assert_phase(self) -> model.SectionContents:
        return phase_contents(self._assert_phase())

    def cleanup_phase(self) -> model.SectionContents:
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
