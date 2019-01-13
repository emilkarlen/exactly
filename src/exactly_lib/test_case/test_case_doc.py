from typing import Sequence

from exactly_lib.section_document.model import SectionContents, ElementType, SectionContentElement, Instruction
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction


class TestCaseOfInstructions(tuple):
    def __new__(cls,
                configuration_phase: Sequence[ConfigurationPhaseInstruction],
                setup_phase: Sequence[SetupPhaseInstruction],
                act_phase: Sequence[ActPhaseInstruction],
                before_assert_phase: Sequence[BeforeAssertPhaseInstruction],
                assert_phase: Sequence[AssertPhaseInstruction],
                cleanup_phase: Sequence[CleanupPhaseInstruction]):
        return tuple.__new__(cls, (configuration_phase,
                                   setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def configuration_phase(self) -> Sequence[ConfigurationPhaseInstruction]:
        return self[0]

    @property
    def setup_phase(self) -> Sequence[SetupPhaseInstruction]:
        return self[1]

    @property
    def act_phase(self) -> Sequence[ActPhaseInstruction]:
        return self[2]

    @property
    def before_assert_phase(self) -> Sequence[BeforeAssertPhaseInstruction]:
        return self[3]

    @property
    def assert_phase(self) -> Sequence[AssertPhaseInstruction]:
        return self[4]

    @property
    def cleanup_phase(self) -> Sequence[CleanupPhaseInstruction]:
        return self[5]


class TestCase(tuple):
    def __new__(cls,
                configuration_phase: SectionContents,
                setup_phase: SectionContents,
                act_phase: SectionContents,
                before_assert_phase: SectionContents,
                assert_phase: SectionContents,
                cleanup_phase: SectionContents):
        TestCase.__assert_instruction_class(configuration_phase,
                                            ConfigurationPhaseInstruction)
        TestCase.__assert_instruction_class(setup_phase,
                                            SetupPhaseInstruction)
        TestCase.__assert_instruction_class(act_phase,
                                            ActPhaseInstruction)
        TestCase.__assert_instruction_class(before_assert_phase,
                                            BeforeAssertPhaseInstruction)
        TestCase.__assert_instruction_class(assert_phase,
                                            AssertPhaseInstruction)
        TestCase.__assert_instruction_class(cleanup_phase,
                                            CleanupPhaseInstruction)
        return tuple.__new__(cls, (configuration_phase,
                                   setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def configuration_phase(self) -> SectionContents:
        return self[0]

    @property
    def setup_phase(self) -> SectionContents:
        return self[1]

    @property
    def act_phase(self) -> SectionContents:
        return self[2]

    @property
    def before_assert_phase(self) -> SectionContents:
        return self[3]

    @property
    def assert_phase(self) -> SectionContents:
        return self[4]

    @property
    def cleanup_phase(self) -> SectionContents:
        return self[5]

    def as_test_case_of_instructions(self) -> TestCaseOfInstructions:
        return TestCaseOfInstructions(
            self.__filter_instructions(self.configuration_phase),
            self.__filter_instructions(self.setup_phase),
            self.__filter_instructions(self.act_phase),
            self.__filter_instructions(self.before_assert_phase),
            self.__filter_instructions(self.assert_phase),
            self.__filter_instructions(self.cleanup_phase),
        )

    @staticmethod
    def __assert_instruction_class(phase_contents: SectionContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                assert isinstance(element.instruction_info.instruction, instruction_class)

    @staticmethod
    def __filter_instructions(section: SectionContents) -> Sequence:
        instruction_elements = filter(_is_instruction_element, section.elements)
        return list(map(_get_instruction, instruction_elements))


def _is_instruction_element(section_element: SectionContentElement) -> bool:
    return section_element.element_type is ElementType.INSTRUCTION


def _get_instruction(section_element: SectionContentElement) -> Instruction:
    return section_element.instruction_info.instruction
