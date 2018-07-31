from typing import List

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.section_document import model
from exactly_lib.section_document.element_builder import SectionContentElementBuilder, SourceLocationBuilder
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import \
    TestCaseGeneratorForPartialExecutionBase, PartialPhase
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from exactly_lib_test.execution.test_resources.execution_recording.recording_instructions import \
    RecordingInstructionsFactory
from exactly_lib_test.execution.test_resources.instruction_test_resources import act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import instruction_line_constructor, \
    phase_contents


class TestCaseGeneratorForExecutionRecording(TestCaseGeneratorForPartialExecutionBase):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__()
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = ListRecorder()
        self.ilc = instruction_line_constructor()
        self.recording_instructions = RecordingInstructionsFactory(self.__recorder)
        self.__recorders = {
            PartialPhase.SETUP: self._new_setup_instruction,
            PartialPhase.BEFORE_ASSERT: self._new_before_assert_instruction,
            PartialPhase.ASSERT: self._new_assert_instruction,
            PartialPhase.CLEANUP: self._new_cleanup_instruction
        }
        self._element_builder = SectionContentElementBuilder(SourceLocationBuilder())
        self.__extra = {}
        for ph in PartialPhase:
            self.__extra[ph] = []
        self.__the_extra = {}

    def add(self, phase: PartialPhase, instruction: TestCaseInstruction):
        self.__extra[phase].append(instruction)
        return self

    def the_extra(self, phase: PartialPhase) -> List[SectionContentElement]:
        if phase not in self.__the_extra:
            self.__the_extra[phase] = self.ilc.apply_list(self.__extra[phase])
        return self.__the_extra[phase]

    def recorder_for(self, phase: PartialPhase) -> model.SectionContentElement:
        return self.ilc.apply(self.__recorders[phase]())

    @property
    def recorder(self) -> ListRecorder:
        return self.__recorder

    def phase_contents_for(self, phase: PartialPhase) -> model.SectionContents:
        return phase_contents(self._all_elements_for(phase))

    def _all_elements_for(self, phase: PartialPhase) -> List[SectionContentElement]:
        raise NotImplementedError()

    def _new_setup_instruction(self):
        return self.recording_instructions.new_setup_instruction(phase_step.SETUP__VALIDATE_SYMBOLS,
                                                                 phase_step.SETUP__VALIDATE_PRE_SDS,
                                                                 phase_step.SETUP__MAIN,
                                                                 phase_step.SETUP__VALIDATE_POST_SETUP)

    def _new_before_assert_instruction(self):
        return self.recording_instructions.new_before_assert_instruction(phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                                                                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
                                                                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                                                                         phase_step.BEFORE_ASSERT__MAIN)

    def _new_assert_instruction(self):
        return self.recording_instructions.new_assert_instruction(phase_step.ASSERT__VALIDATE_SYMBOLS,
                                                                  phase_step.ASSERT__VALIDATE_PRE_SDS,
                                                                  phase_step.ASSERT__VALIDATE_POST_SETUP,
                                                                  phase_step.ASSERT__MAIN)

    def _new_cleanup_instruction(self):
        return self.recording_instructions.new_cleanup_instruction(phase_step.CLEANUP__VALIDATE_SYMBOLS,
                                                                   phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                                                   phase_step.CLEANUP__MAIN)


class TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None,
                 act_phase_source: LineSequence = LineSequence(99, ('act phase line',))):
        super().__init__(recorder)
        self.act_phase_source = act_phase_source

    def phase_contents_for_act(self, act_phase: PartialPhase) -> model.SectionContents:
        return phase_contents(
            [self._element_builder.new_instruction(self.act_phase_source,
                                                   act_phase_instruction_with_source(self.act_phase_source))])

    def _all_elements_for(self, phase: PartialPhase) -> List[SectionContentElement]:
        return [self.recorder_for(phase)] + self.the_extra(phase)


class TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None,
                 act_phase_source: LineSequence = LineSequence(99, ('act phase line',))):
        super().__init__(recorder)
        self.act_phase_source = act_phase_source

    def phase_contents_for_act(self, act_phase: PartialPhase) -> model.SectionContents:
        return phase_contents(
            [self._element_builder.new_instruction(self.act_phase_source,
                                                   act_phase_instruction_with_source(self.act_phase_source))])

    def _all_elements_for(self, phase: PartialPhase) -> list:
        return [self.recorder_for(phase)] + self.the_extra(phase) + [self.recorder_for(phase)]
