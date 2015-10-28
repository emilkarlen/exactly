from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction
from shellcheck_lib_test.execution.full_execution.util import recording_instructions_for_sequence_tests as instr
from shellcheck_lib_test.execution.full_execution.util.recording_instructions_for_sequence_tests import \
    SetupInstructionThatRecordsStringInList, AssertInternalInstructionThatRecordsStringInList, \
    AssertInstructionThatRecordsStringInRecordFile
from shellcheck_lib_test.execution.util.test_case_generation import TestCaseGeneratorBase
from shellcheck_lib.execution import phase_step
from shellcheck_lib_test.execution.util import instruction_adapter


class TestCaseGeneratorForExecutionRecording(TestCaseGeneratorBase):
    def __init__(self,
                 recorder: instr.ListRecorder=None):
        super().__init__()
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = instr.ListRecorder()

    def _anonymous_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AnonymousPhaseInstruction)
        """
        return []

    def _setup_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return []

    def _act_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return []

    def _assert_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return []

    def _cleanup_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return []

    @property
    def recorder(self) -> instr.ListRecorder:
        return self.__recorder

    @property
    def internal_instruction_recorder(self) -> list:
        return self.__recorder.recorded_elements

    def _anonymous_phase(self) -> list:
        return self._anonymous_phase_recording() + \
               self._anonymous_phase_extra()

    def _setup_phase(self) -> list:
        return self._setup_phase_recording() + \
               self._setup_phase_extra()

    def _act_phase(self) -> list:
        return self._act_phase_recording() + \
               self._act_phase_extra()

    def _assert_phase(self) -> list:
        return self._assert_phase_recording() + \
               self._assert_phase_extra()

    def _cleanup_phase(self) -> list:
        return self._cleanup_phase_recording() + \
               self._cleanup_phase_extra()

    def _anonymous_phase_recording(self) -> list:
        return list(map(self._next_instruction_line,
                        [
                            self._new_anonymous_internal_recorder(phase_step.ANONYMOUS)
                        ]))

    def _setup_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            self._new_setup_internal_recorder(phase_step.SETUP__PRE_VALIDATE,
                                                              phase_step.SETUP__EXECUTE,
                                                              phase_step.SETUP__POST_VALIDATE),
                            instr.SetupInstructionThatRecordsStringInRecordFile(
                                phase_step.SETUP__EXECUTE,
                                phase_step.SETUP__POST_VALIDATE),
                        ]))

    def _act_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            self._new_act_internal_recorder(phase_step.ACT__VALIDATE,
                                                            phase_step.ACT__SCRIPT_GENERATION),
                            instr.ActInstructionThatRecordsStringInRecordFile(
                                phase_step.ACT__VALIDATE,
                                phase_step.ACT__SCRIPT_GENERATION),
                            instr.ActInstructionThatGeneratesScriptThatRecordsStringInRecordFile(
                                phase_step.ACT__SCRIPT_EXECUTION),
                        ]))

    def _assert_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            self._new_assert_internal_recorder(phase_step.ASSERT__VALIDATE,
                                                               phase_step.ASSERT__EXECUTE),
                            AssertInstructionThatRecordsStringInRecordFile(phase_step.ASSERT__VALIDATE,
                                                                           phase_step.ASSERT__EXECUTE),
                        ]))

    def _cleanup_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            instruction_adapter.as_cleanup(
                                instr.InternalInstructionThatRecordsStringInList(
                                    self.__recorder_of(phase_step.CLEANUP))),
                            instruction_adapter.as_cleanup(
                                instr.InternalInstructionThatRecordsStringInRecordFile(phase_step.CLEANUP)),
                        ]))

    def _new_anonymous_internal_recorder(self, text: str) -> SetupPhaseInstruction:
        return instr.AnonymousInternalInstructionThatRecordsStringInList(self.__recorder_of(text))

    def _new_setup_internal_recorder(self,
                                     text_for_pre_validate: str,
                                     text_for_execute: str,
                                     text_for_post_validate: str) -> SetupPhaseInstruction:
        return SetupInstructionThatRecordsStringInList(self.__recorder_of(text_for_pre_validate),
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
        return AssertInternalInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                                self.__recorder_of(text_for_execute))

    def _new_cleanup_internal_recorder(self, text: str) -> CleanupPhaseInstruction:
        return instruction_adapter.as_cleanup(
            instr.InternalInstructionThatRecordsStringInList(self.__recorder_of(text)))

    def __recorder_of(self, element: str) -> instr.ListElementRecorder:
        return self.__recorder.recording_of(element)


class TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 recorder: instr.ListRecorder=None):
        super().__init__(recorder)
        self.__anonymous_extra = []
        self.__setup_extra = []
        self.__act_extra = []
        self.__assert_extra = []
        self.__cleanup_extra = []

        self.__the_anonymous_extra = None
        self.__the_setup_extra = None
        self.__the_act_extra = None
        self.__the_assert_extra = None
        self.__the_cleanup_extra = None

    def _anonymous_phase_extra(self) -> list:
        self.__the_anonymous_extra = list(map(self._next_instruction_line, self.__anonymous_extra))
        return self.__the_anonymous_extra

    def _setup_phase_extra(self) -> list:
        self.__the_setup_extra = list(map(self._next_instruction_line, self.__setup_extra))
        return self.__the_setup_extra

    def _act_phase_extra(self) -> list:
        self.__the_act_extra = list(map(self._next_instruction_line, self.__act_extra))
        return self.__the_act_extra

    def _assert_phase_extra(self) -> list:
        self.__the_assert_extra = list(map(self._next_instruction_line, self.__assert_extra))
        return self.__the_assert_extra

    def _cleanup_phase_extra(self) -> list:
        self.__the_cleanup_extra = list(map(self._next_instruction_line, self.__cleanup_extra))
        return self.__the_cleanup_extra

    def add_anonymous(self, instruction: AnonymousPhaseInstruction):
        self.__anonymous_extra.append(instruction)
        return self

    def add_anonymous_internal_recorder_of(self, text: str):
        self.__anonymous_extra.append(self._new_anonymous_internal_recorder(text))
        return self

    def add_setup(self, instruction: SetupPhaseInstruction):
        self.__setup_extra.append(instruction)
        return self

    # def add_setup_internal_recorder_of(self, text: str):
    #     self.__setup_extra.append(self._new_setup_internal_recorder(text))
    #     return self

    def add_act(self, instruction: ActPhaseInstruction):
        self.__act_extra.append(instruction)
        return self

    # def add_act_internal_recorder_of(self, text: str):
    #     self.__act_extra.append(self._new_act_internal_recorder(text))
    #     return self

    def add_assert(self, instruction: AssertPhaseInstruction):
        self.__assert_extra.append(instruction)
        return self

    # def add_assert_internal_recorder_of(self, text: str):
    #     self.__assert_extra.append(self._new_assert_internal_recorder(text))
    #     return self
    #
    def add_cleanup(self, instruction: CleanupPhaseInstruction):
        self.__cleanup_extra.append(instruction)
        return self

    def add_cleanup_internal_recorder_of(self, text: str):
        self.__cleanup_extra.append(self._new_cleanup_internal_recorder(text))
        return self

    @property
    def the_anonymous_phase_extra(self) -> list:
        """
        :rtype [PhaseContentElement]
        """
        self.test_case
        return self.__the_anonymous_extra

    @property
    def the_setup_phase_extra(self) -> list:
        """
        :rtype [PhaseContentElement]
        """
        self.test_case
        return self.__the_setup_extra

    @property
    def the_act_phase_extra(self) -> list:
        """
        :rtype [PhaseContentElement]
        """
        self.test_case
        return self.__the_act_extra

    @property
    def the_assert_phase_extra(self) -> list:
        """
        :rtype [PhaseContentElement]
        """
        self.test_case
        return self.__the_assert_extra

    @property
    def the_cleanup_phase_extra(self) -> list:
        """
        :rtype [PhaseContentElement]
        """
        self.test_case
        return self.__the_cleanup_extra
