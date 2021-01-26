from typing import Sequence, TypeVar, Generic, Callable

from exactly_lib.section_document.model import SectionContents, ElementType, SectionContentElement, Instruction, \
    InstructionInfo
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction

T = TypeVar('T')


class ElementWithSourceLocation(Generic[T]):
    def __init__(self,
                 source_location_info: SourceLocationInfo,
                 value: T):
        self._value = value
        self._source_location_info = source_location_info

    @property
    def value(self) -> T:
        return self._value

    @property
    def source_location_info(self) -> SourceLocationInfo:
        return self._source_location_info


class TestCaseOfInstructions(tuple):
    def __new__(cls,
                configuration_phase: Sequence[ElementWithSourceLocation[ConfigurationPhaseInstruction]],
                setup_phase: Sequence[ElementWithSourceLocation[SetupPhaseInstruction]],
                act_phase: Sequence[ElementWithSourceLocation[ActPhaseInstruction]],
                before_assert_phase: Sequence[ElementWithSourceLocation[BeforeAssertPhaseInstruction]],
                assert_phase: Sequence[ElementWithSourceLocation[AssertPhaseInstruction]],
                cleanup_phase: Sequence[ElementWithSourceLocation[CleanupPhaseInstruction]]):
        return tuple.__new__(cls, (configuration_phase,
                                   setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def configuration_phase(self) -> Sequence[ElementWithSourceLocation[ConfigurationPhaseInstruction]]:
        return self[0]

    @property
    def setup_phase(self) -> Sequence[ElementWithSourceLocation[SetupPhaseInstruction]]:
        return self[1]

    @property
    def act_phase(self) -> Sequence[ElementWithSourceLocation[ActPhaseInstruction]]:
        return self[2]

    @property
    def before_assert_phase(self) -> Sequence[ElementWithSourceLocation[BeforeAssertPhaseInstruction]]:
        return self[3]

    @property
    def assert_phase(self) -> Sequence[ElementWithSourceLocation[AssertPhaseInstruction]]:
        return self[4]

    @property
    def cleanup_phase(self) -> Sequence[ElementWithSourceLocation[CleanupPhaseInstruction]]:
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
            filter_instructions_with_source_location(_get_configuration_phase_instruction, self.configuration_phase),
            filter_instructions_with_source_location(_get_setup_phase_instruction, self.setup_phase),
            filter_instructions_with_source_location(_get_act_phase_instruction, self.act_phase),
            filter_instructions_with_source_location(_get_before_assert_phase_instruction, self.before_assert_phase),
            filter_instructions_with_source_location(_get_assert_phase_instruction, self.assert_phase),
            filter_instructions_with_source_location(_get_cleanup_phase_instruction, self.cleanup_phase),
        )

    @staticmethod
    def __assert_instruction_class(phase_contents: SectionContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                assert isinstance(element.instruction_info.instruction, instruction_class)


def filter_instructions_with_source_location(get_instruction: Callable[[InstructionInfo], T],
                                             section: SectionContents,
                                             ) -> Sequence[ElementWithSourceLocation[T]]:
    def get_element(section_element: SectionContentElement) -> ElementWithSourceLocation[T]:
        instruction = get_instruction(section_element.instruction_info)
        return ElementWithSourceLocation(
            section_element.source_location_info,
            instruction
        )

    instruction_elements = filter(_is_instruction_element, section.elements)

    return list(map(get_element, instruction_elements))


def _is_instruction_element(section_element: SectionContentElement) -> bool:
    return section_element.element_type is ElementType.INSTRUCTION


def _get_instruction(section_element: SectionContentElement) -> Instruction:
    return section_element.instruction_info.instruction


def _get_configuration_phase_instruction(info: InstructionInfo) -> ConfigurationPhaseInstruction:
    instruction = info.instruction
    assert isinstance(instruction, ConfigurationPhaseInstruction)
    return instruction


def _get_setup_phase_instruction(info: InstructionInfo) -> SetupPhaseInstruction:
    instruction = info.instruction
    assert isinstance(instruction, SetupPhaseInstruction)
    return instruction


def _get_act_phase_instruction(info: InstructionInfo) -> ActPhaseInstruction:
    instruction = info.instruction
    assert isinstance(instruction, ActPhaseInstruction)
    return instruction


def _get_before_assert_phase_instruction(info: InstructionInfo) -> BeforeAssertPhaseInstruction:
    instruction = info.instruction
    assert isinstance(instruction, BeforeAssertPhaseInstruction)
    return instruction


def _get_assert_phase_instruction(info: InstructionInfo) -> AssertPhaseInstruction:
    instruction = info.instruction
    assert isinstance(instruction, AssertPhaseInstruction)
    return instruction


def _get_cleanup_phase_instruction(info: InstructionInfo) -> CleanupPhaseInstruction:
    instruction = info.instruction
    assert isinstance(instruction, CleanupPhaseInstruction)
    return instruction
