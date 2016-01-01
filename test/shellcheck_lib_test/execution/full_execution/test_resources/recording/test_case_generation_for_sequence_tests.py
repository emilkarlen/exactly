from shellcheck_lib.document import model
from shellcheck_lib.execution import phases, phase_step
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_generator import \
    TestCaseGeneratorForFullExecutionBase
from shellcheck_lib_test.execution.test_resources import instruction_adapter
from shellcheck_lib_test.execution.test_resources.execution_recording import \
    recording_instructions as instr
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder, ListElementRecorder
from shellcheck_lib_test.execution.test_resources.test_case_generation import instruction_line_constructor, \
    TestCaseInstructionsForFullExecution, phase_contents


class TestCaseGeneratorForExecutionRecording(TestCaseGeneratorForFullExecutionBase):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__()
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = ListRecorder()
        self.ilc = instruction_line_constructor()

        self.__recorders = {}
        r = self.__recorders
        r[phases.ANONYMOUS] = self._new_anonymous_internal_recorder(phase_step.ANONYMOUS)
        r[phases.SETUP] = self._new_setup_internal_recorder(phase_step.SETUP__PRE_VALIDATE,
                                                            phase_step.SETUP__EXECUTE,
                                                            phase_step.SETUP__POST_VALIDATE)
        r[phases.ACT] = self._new_act_internal_recorder(phase_step.ACT__VALIDATE,
                                                        phase_step.ACT__SCRIPT_GENERATE)
        r[phases.ASSERT] = self._new_assert_internal_recorder(phase_step.ASSERT__VALIDATE,
                                                              phase_step.ASSERT__EXECUTE)
        r[phases.CLEANUP] = instruction_adapter.as_cleanup(
                instr.InternalInstructionThatRecordsStringInList(
                        self.__recorder_of(phase_step.CLEANUP)))

    def recorders_for(self, phase: phases.Phase) -> list:
        return [self.ilc.apply(self.__recorders[phase])]

    def the_extra(self, phase: phases.Phase) -> list:
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

    def phase_contents_for(self, phase: phases.Phase) -> model.PhaseContents:
        return phase_contents(self._all_elements_for(phase))

    def _all_elements_for(self, phase: phases.Phase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        return self.recorders_for(phase) + self.the_extra(phase)

    def _new_anonymous_internal_recorder(self, text: str) -> SetupPhaseInstruction:
        return instr.AnonymousInternalInstructionThatRecordsStringInList(self.__recorder_of(text))

    def _new_setup_internal_recorder(self,
                                     text_for_pre_validate: str,
                                     text_for_execute: str,
                                     text_for_post_validate: str) -> SetupPhaseInstruction:
        return instr.SetupInstructionThatRecordsStringInList(self.__recorder_of(text_for_pre_validate),
                                                             self.__recorder_of(text_for_execute),
                                                             self.__recorder_of(text_for_post_validate))

    def _new_act_internal_recorder(self,
                                   text_for_validate: str,
                                   text_for_execute: str) -> ActPhaseInstruction:
        return instr.ActInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                           self.__recorder_of(text_for_execute))

    def _new_assert_internal_recorder(self,
                                      text_for_validate: str,
                                      text_for_execute: str) -> AssertPhaseInstruction:
        return instr.AssertInternalInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                                      self.__recorder_of(text_for_execute))

    def _new_cleanup_internal_recorder(self, text: str) -> CleanupPhaseInstruction:
        return instruction_adapter.as_cleanup(
                instr.InternalInstructionThatRecordsStringInList(self.__recorder_of(text)))

    def __recorder_of(self, element: str) -> ListElementRecorder:
        return self.__recorder.recording_of(element)


class TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: ListRecorder = None):
        super().__init__(recorder)
        self.__extra = TestCaseInstructionsForFullExecution()

        self.__extra = {}
        for ph in phases.ALL:
            self.__extra[ph] = []
        self.__the_extra = {}

    def add(self, phase: phases.Phase, instruction: AnonymousPhaseInstruction):
        self.__extra[phase].append(instruction)
        return self

    def add_anonymous_internal_recorder_of(self, text: str):
        self.__extra[phases.ANONYMOUS].append(self._new_anonymous_internal_recorder(text))
        return self

    def add_cleanup_internal_recorder_of(self, text: str):
        self.__extra[phases.CLEANUP].append(self._new_cleanup_internal_recorder(text))
        return self

    def the_extra(self, phase: phases.Phase) -> list:
        """
        :rtype [PhaseContentElement]
        """
        if phase not in self.__the_extra:
            self.__the_extra[phase] = self.ilc.apply_list(self.__extra[phase])
        return self.__the_extra[phase]
