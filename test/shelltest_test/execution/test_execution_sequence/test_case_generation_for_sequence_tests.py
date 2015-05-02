from shelltest.phase_instr.model import PhaseContentElement
from shelltest_test.execution.test_execution_sequence import recording_instructions_for_sequence_tests as instr
from shelltest_test.execution.util.test_case_generation import TestCaseGeneratorBase

__author__ = 'emil'

from shelltest.execution import phase_step
from shelltest.exec_abs_syn import instructions
from shelltest.phase_instr import model
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest_test.execution.util import instruction_adapter


class TestCaseGeneratorForExecutionRecording(TestCaseGeneratorBase):
    def __init__(self):
        super().__init__()
        self.__recorder = []

    def _generate(self) -> abs_syn_gen.TestCase:
        return abs_syn_gen.TestCase(
            self.__from(self._anonymous_phase_recording() +
                        self._anonymous_phase_extra()),
            self.__from(self._setup_phase_recording() +
                        self._setup_phase_extra()),
            self.__from(self._act_phase_recording() +
                        self._act_phase_extra()),
            self.__from(self._assert_phase_recording() +
                        self._assert_phase_extra()),
            self.__from(self._cleanup_phase_recording() +
                        self._cleanup_phase_extra())
        )

    @property
    def internal_instruction_recorder(self) -> list:
        return self.__recorder

    @staticmethod
    def __from(phase_content_elements: list) -> model.PhaseContents:
        return model.PhaseContents(tuple(phase_content_elements))

    def _anonymous_phase_recording(self) -> list:
        return list(map(self._next_instruction_line,
                        [
                            instr.AnonymousInternalInstructionThatRecordsStringInList(
                                self.__recorder_of(phase_step.ANONYMOUS))
                        ]))

    def _anonymous_phase_extra(self) -> list:
        return []

    def _setup_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            instruction_adapter.as_setup(
                                instr.InternalInstructionThatRecordsStringInList(self.__recorder_of(phase_step.SETUP))),
                            instruction_adapter.as_setup(
                                instr.InternalInstructionThatRecordsStringInRecordFile(phase_step.SETUP)),
                        ]))

    def _setup_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return []

    def _act_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            instr.ActInstructionThatRecordsStringInList(
                                self.__recorder_of(phase_step.ACT__SCRIPT_GENERATION)),
                            instr.ActInstructionThatRecordsStringInRecordFile(phase_step.ACT__SCRIPT_GENERATION),
                            instr.ActInstructionThatRecordsStringInRecordFile(phase_step.ACT__SCRIPT_EXECUTION),
                        ]))

    def _act_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return []

    def _assert_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return list(map(self._next_instruction_line,
                        [
                            instruction_adapter.as_assert(
                                instr.InternalInstructionThatRecordsStringInList(
                                    self.__recorder_of(phase_step.ASSERT))),
                            instruction_adapter.as_assert(
                                instr.InternalInstructionThatRecordsStringInRecordFile(phase_step.ASSERT)),
                        ]))

    def _assert_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return []

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

    def _cleanup_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return []

    def __recorder_of(self, s: str) -> instr.ListRecorder:
        return instr.ListRecorder(self.__recorder,
                                  s)


class TestCaseThatRecordsExecutionWithSingleExtraInstruction(TestCaseGeneratorForExecutionRecording):
    def __init__(self,
                 anonymous_extra: instructions.AnonymousPhaseInstruction=None,
                 setup_extra: instructions.SetupPhaseInstruction=None,
                 act_extra: instructions.ActPhaseInstruction=None,
                 assert_extra: instructions.AssertPhaseInstruction=None,
                 cleanup_extra: instructions.CleanupPhaseInstruction=None):
        super().__init__()
        self.__anonymous_extra = anonymous_extra
        self.__setup_extra = setup_extra
        self.__act_extra = act_extra
        self.__assert_extra = assert_extra
        self.__cleanup_extra = cleanup_extra

        self.__the_anonymous_extra = None
        self.__the_setup_extra = None
        self.__the_act_extra = None
        self.__the_assert_extra = None
        self.__the_cleanup_extra = None

    def _anonymous_phase_extra(self) -> list:
        if self.__anonymous_extra:
            self.__the_anonymous_extra = self._next_instruction_line(self.__anonymous_extra)
            return [self.__the_anonymous_extra]
        else:
            return []

    def _setup_phase_extra(self) -> list:
        if self.__setup_extra:
            self.__the_setup_extra = self._next_instruction_line(self.__setup_extra)
            return [self.__the_setup_extra]
        else:
            return []

    def _act_phase_extra(self) -> list:
        if self.__act_extra:
            self.__the_act_extra = self._next_instruction_line(self.__act_extra)
            return [self.__the_act_extra]
        else:
            return []

    def _assert_phase_extra(self) -> list:
        if self.__assert_extra:
            self.__the_assert_extra = self._next_instruction_line(self.__assert_extra)
            return [self.__the_assert_extra]
        else:
            return []

    def _cleanup_phase_extra(self) -> list:
        if self.__cleanup_extra:
            self.__the_cleanup_extra = self._next_instruction_line(self.__cleanup_extra)
            return [self.__the_cleanup_extra]
        else:
            return []

    @property
    def the_anonymous_phase_extra(self) -> PhaseContentElement:
        self.test_case
        return self.__the_anonymous_extra

    @property
    def the_setup_phase_extra(self) -> PhaseContentElement:
        self.test_case
        return self.__the_setup_extra

    @property
    def the_act_phase_extra(self) -> PhaseContentElement:
        self.test_case
        return self.__the_act_extra

    @property
    def the_assert_phase_extra(self) -> PhaseContentElement:
        self.test_case
        return self.__the_assert_extra

    @property
    def the_cleanup_phase_extra(self) -> PhaseContentElement:
        self.test_case
        return self.__the_cleanup_extra

