from shelltest_test.execution.test_full_execution.util import recording_instructions_for_sequence_tests as instr
from shelltest_test.execution.test_full_execution.util.recording_instructions_for_sequence_tests import \
    SetupInternalInstructionThatRecordsStringInList, AssertInternalInstructionThatRecordsStringInList, \
    AssertInstructionThatRecordsStringInRecordFile
from shelltest_test.execution.util.test_case_generation import TestCaseGeneratorBase
from shelltest.execution import phase_step
from shelltest.exec_abs_syn import instructions
from shelltest_test.execution.util import instruction_adapter


class TestCaseGeneratorForExecutionRecording(TestCaseGeneratorBase):
    def __init__(self):
        super().__init__()
        self.__recorder = []

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
    def internal_instruction_recorder(self) -> list:
        return self.__recorder

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
                            self._new_setup_internal_recorder(phase_step.SETUP__VALIDATE,
                                                              phase_step.SETUP__EXECUTE),
                            instruction_adapter.as_setup(
                                instr.InternalInstructionThatRecordsStringInRecordFile(phase_step.SETUP__EXECUTE)),
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

    def _new_anonymous_internal_recorder(self, text: str) -> instructions.SetupPhaseInstruction:
        return instr.AnonymousInternalInstructionThatRecordsStringInList(self.__recorder_of(text))

    def _new_setup_internal_recorder(self,
                                     text_for_validate: str,
                                     text_for_execute: str) -> instructions.SetupPhaseInstruction:
        return SetupInternalInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                               self.__recorder_of(text_for_execute))

    def _new_act_internal_recorder(self,
                                   text_for_validate: str,
                                   text_for_execute: str) -> instructions.ActPhaseInstruction:
        return instr.ActInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                           self.__recorder_of(text_for_execute))

    def _new_assert_internal_recorder(self,
                                      text_for_validate: str,
                                      text_for_execute: str) -> instructions.AssertPhaseInstruction:
        return AssertInternalInstructionThatRecordsStringInList(self.__recorder_of(text_for_validate),
                                                                self.__recorder_of(text_for_execute))

    def _new_cleanup_internal_recorder(self, text: str) -> instructions.CleanupPhaseInstruction:
        return instruction_adapter.as_cleanup(
            instr.InternalInstructionThatRecordsStringInList(self.__recorder_of(text)))

    def __recorder_of(self, s: str) -> instr.ListRecorder:
        return instr.ListRecorder(self.__recorder,
                                  s)


class TestCaseThatRecordsExecutionWithExtraInstructionList(TestCaseGeneratorForExecutionRecording):
    def __init__(self):
        super().__init__()
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

    def add_anonymous(self, instruction: instructions.AnonymousPhaseInstruction):
        self.__anonymous_extra.append(instruction)
        return self

    def add_anonymous_internal_recorder_of(self, text: str):
        self.__anonymous_extra.append(self._new_anonymous_internal_recorder(text))
        return self

    def add_setup(self, instruction: instructions.SetupPhaseInstruction):
        self.__setup_extra.append(instruction)
        return self

    def add_setup_internal_recorder_of(self, text: str):
        self.__setup_extra.append(self._new_setup_internal_recorder(text))
        return self

    def add_act(self, instruction: instructions.ActPhaseInstruction):
        self.__act_extra.append(instruction)
        return self

    def add_act_internal_recorder_of(self, text: str):
        self.__act_extra.append(self._new_act_internal_recorder(text))
        return self

    def add_assert(self, instruction: instructions.AssertPhaseInstruction):
        self.__assert_extra.append(instruction)
        return self

    def add_assert_internal_recorder_of(self, text: str):
        self.__assert_extra.append(self._new_assert_internal_recorder(text))
        return self

    def add_cleanup(self, instruction: instructions.CleanupPhaseInstruction):
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

