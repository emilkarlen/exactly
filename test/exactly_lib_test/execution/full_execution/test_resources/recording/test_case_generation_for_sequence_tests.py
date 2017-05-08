from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.section_document import model
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib_test.execution.full_execution.test_resources.test_case_generator import \
    TestCaseGeneratorForFullExecutionBase
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder, ListElementRecorder
from exactly_lib_test.execution.test_resources.execution_recording.recording_instructions import \
    RecordingInstructionsFactory
from exactly_lib_test.execution.test_resources.instruction_test_resources import act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import instruction_line_constructor, \
    phase_contents


class TestCaseGeneratorForExecutionRecording(TestCaseGeneratorForFullExecutionBase):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__()
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = ListRecorder()
        self.ilc = instruction_line_constructor()

        self.__recording_instructions = RecordingInstructionsFactory(self.__recorder)
        self.__recorders = {
            phase_identifier.CONFIGURATION: self._new_configuration_instruction,
            phase_identifier.SETUP: self._new_setup_instruction,
            phase_identifier.ACT: act_phase_instruction_with_source,
            phase_identifier.BEFORE_ASSERT: self._new_before_assert_instruction,
            phase_identifier.ASSERT: self._new_assert_instruction,
            phase_identifier.CLEANUP: self._new_cleanup_instruction
        }

        self.__extra = {}
        for ph in phase_identifier.ALL:
            self.__extra[ph] = []
        self.__the_extra = {}

    def add(self, phase: phase_identifier.Phase, instruction: TestCaseInstruction):
        self.__extra[phase].append(instruction)
        return self

    def the_extra(self, phase: phase_identifier.Phase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        if phase not in self.__the_extra:
            self.__the_extra[phase] = self.ilc.apply_list(self.__extra[phase])
        return self.__the_extra[phase]

    def recorder_for(self, phase: phase_identifier.Phase) -> SectionContentElement:
        return self.ilc.apply(self.__recorders[phase]())

    @property
    def recorder(self) -> ListRecorder:
        return self.__recorder

    @property
    def internal_instruction_recorder(self) -> list:
        return self.__recorder.recorded_elements

    def phase_contents_for(self, phase: phase_identifier.Phase) -> model.SectionContents:
        return phase_contents(self._all_elements_for(phase))

    def _all_elements_for(self, phase: phase_identifier.Phase) -> list:
        raise NotImplementedError()

    def __recorder_of(self, element: str) -> ListElementRecorder:
        return self.__recorder.recording_of(element)

    def _new_configuration_instruction(self):
        return self.__recording_instructions.new_configuration_instruction(phase_step.CONFIGURATION__MAIN)

    def _new_setup_instruction(self):
        return self.__recording_instructions.new_setup_instruction(phase_step.SETUP__VALIDATE_SYMBOLS,
                                                                   phase_step.SETUP__VALIDATE_PRE_SDS,
                                                                   phase_step.SETUP__MAIN,
                                                                   phase_step.SETUP__VALIDATE_POST_SETUP)

    def _new_before_assert_instruction(self):
        return self.__recording_instructions.new_before_assert_instruction(phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                                                                           phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
                                                                           phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                                                                           phase_step.BEFORE_ASSERT__MAIN)

    def _new_assert_instruction(self):
        return self.__recording_instructions.new_assert_instruction(phase_step.ASSERT__VALIDATE_SYMBOLS,
                                                                    phase_step.ASSERT__VALIDATE_PRE_SDS,
                                                                    phase_step.ASSERT__VALIDATE_POST_SETUP,
                                                                    phase_step.ASSERT__MAIN)

    def _new_cleanup_instruction(self):
        return self.__recording_instructions.new_cleanup_instruction(phase_step.CLEANUP__VALIDATE_SYMBOLS,
                                                                     phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                                                     phase_step.CLEANUP__MAIN)


class TestCaseGeneratorWithRecordingInstrFollowedByExtraInstrsInEachPhase(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__(recorder)

    def _all_elements_for(self, phase: phase_identifier.Phase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        return [self.recorder_for(phase)] + self.the_extra(phase)


class TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__(recorder)

    def _all_elements_for(self, phase: phase_identifier.Phase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        return [self.recorder_for(phase)] + self.the_extra(phase) + [self.recorder_for(phase)]


def test_case_with_two_instructions_in_each_phase() -> TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr:
    return TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr()
