from shellcheck_lib.document import model
from shellcheck_lib.execution import phase_step
from shellcheck_lib.test_case.sections.common import TestCaseInstruction
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import \
    TestCaseGeneratorForPartialExecutionBase, PartialPhase
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from shellcheck_lib_test.execution.test_resources.execution_recording.recording_instructions import \
    RecordingInstructions
from shellcheck_lib_test.execution.test_resources.test_case_generation import instruction_line_constructor, \
    TestCaseInstructionsForFullExecution, phase_contents


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
                recording_instructions.new_setup_instruction(phase_step.SETUP__VALIDATE_PRE_EDS,
                                                             phase_step.SETUP__MAIN,
                                                             phase_step.SETUP__VALIDATE_POST_SETUP),
            PartialPhase.ACT:
                recording_instructions.new_act_instruction(phase_step.ACT__VALIDATE_PRE_EDS,
                                                           phase_step.ACT__VALIDATE_POST_SETUP,
                                                           phase_step.ACT__MAIN),
            PartialPhase.BEFORE_ASSERT:
                recording_instructions.new_before_assert_instruction(phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
                                                                     phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                                                                     phase_step.BEFORE_ASSERT__MAIN),
            PartialPhase.ASSERT:
                recording_instructions.new_assert_instruction(phase_step.ASSERT__VALIDATE_PRE_EDS,
                                                              phase_step.ASSERT__VALIDATE_POST_SETUP,
                                                              phase_step.ASSERT__MAIN),
            PartialPhase.CLEANUP:
                recording_instructions.new_cleanup_instruction(phase_step.CLEANUP__VALIDATE_PRE_EDS,
                                                               phase_step.CLEANUP__MAIN)
        }

    def recorders_for(self, phase: PartialPhase) -> list:
        return [self.ilc.apply(self.__recorders[phase])]

    def the_extra(self, phase: PartialPhase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        raise NotImplementedError()

    @property
    def recorder(self) -> ListRecorder:
        return self.__recorder

    @property
    def internal_instruction_recorder(self) -> list:
        return self.__recorder.recorded_elements

    def phase_contents_for(self, phase: PartialPhase) -> model.PhaseContents:
        return phase_contents(self._all_elements_for(phase))

    def _all_elements_for(self, phase: PartialPhase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        return self.recorders_for(phase) + self.the_extra(phase)


class TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__(recorder)
        self.__extra = TestCaseInstructionsForFullExecution()

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
