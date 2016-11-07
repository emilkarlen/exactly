from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.section_document import model
from exactly_lib.section_document.model import new_instruction_e
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import \
    TestCaseGeneratorForPartialExecutionBase, PartialPhase
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from exactly_lib_test.execution.test_resources.execution_recording.recording_instructions import \
    RecordingInstructions
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
        recording_instructions = RecordingInstructions(self.__recorder)
        self.__recorders = {
            PartialPhase.SETUP:
                recording_instructions.new_setup_instruction(phase_step.SETUP__VALIDATE_PRE_SDS,
                                                             phase_step.SETUP__MAIN,
                                                             phase_step.SETUP__VALIDATE_POST_SETUP),
            PartialPhase.BEFORE_ASSERT:
                recording_instructions.new_before_assert_instruction(phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
                                                                     phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                                                                     phase_step.BEFORE_ASSERT__MAIN),
            PartialPhase.ASSERT:
                recording_instructions.new_assert_instruction(phase_step.ASSERT__VALIDATE_PRE_SDS,
                                                              phase_step.ASSERT__VALIDATE_POST_SETUP,
                                                              phase_step.ASSERT__MAIN),
            PartialPhase.CLEANUP:
                recording_instructions.new_cleanup_instruction(phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                                               phase_step.CLEANUP__MAIN)
        }
        self.__extra = {}
        for ph in PartialPhase:
            self.__extra[ph] = []
        self.__the_extra = {}

    def add(self, phase: PartialPhase, instruction: TestCaseInstruction):
        self.__extra[phase].append(instruction)
        return self

    def the_extra(self, phase: PartialPhase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        if phase not in self.__the_extra:
            self.__the_extra[phase] = self.ilc.apply_list(self.__extra[phase])
        return self.__the_extra[phase]

    def recorder_for(self, phase: PartialPhase) -> list:
        return self.ilc.apply(self.__recorders[phase])

    @property
    def recorder(self) -> ListRecorder:
        return self.__recorder

    @property
    def internal_instruction_recorder(self) -> list:
        return self.__recorder.recorded_elements

    def phase_contents_for(self, phase: PartialPhase) -> model.SectionContents:
        return phase_contents(self._all_elements_for(phase))

    def _all_elements_for(self, phase: PartialPhase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        raise NotImplementedError()


class TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None,
                 act_phase_source: LineSequence = LineSequence(99, ('act phase line',))):
        super().__init__(recorder)
        self.act_phase_source = act_phase_source

    def phase_contents_for_act(self, act_phase: PartialPhase) -> model.SectionContents:
        return phase_contents(
            [new_instruction_e(self.act_phase_source,
                               act_phase_instruction_with_source(self.act_phase_source))])

    def _all_elements_for(self, phase: PartialPhase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        return [self.recorder_for(phase)] + self.the_extra(phase)


class TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None,
                 act_phase_source: LineSequence = LineSequence(99, ('act phase line',))):
        super().__init__(recorder)
        self.act_phase_source = act_phase_source

    def phase_contents_for_act(self, act_phase: PartialPhase) -> model.SectionContents:
        return phase_contents(
            [new_instruction_e(self.act_phase_source,
                               act_phase_instruction_with_source(self.act_phase_source))])

    def _all_elements_for(self, phase: PartialPhase) -> list:
        return [self.recorder_for(phase)] + self.the_extra(phase) + [self.recorder_for(phase)]
