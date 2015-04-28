"""
Functionality for generating a Shell Script from a parsed Test Case file.
"""
__author__ = 'emil'

from shelltest.exec_abs_syn import instructions
from shelltest.phase_instr.model import PhaseContents


class TestCase(tuple):
    def __new__(cls,
                anonymous_phase: PhaseContents,
                setup_phase: PhaseContents,
                act_phase: PhaseContents,
                assert_phase: PhaseContents,
                cleanup_phase: PhaseContents):
        TestCase.__assert_instruction_class(anonymous_phase, instructions.AnonymousPhaseInstruction)
        TestCase.__assert_instruction_class(setup_phase, instructions.SetupPhaseInstruction)
        TestCase.__assert_instruction_class(act_phase, instructions.ActPhaseInstruction)
        TestCase.__assert_instruction_class(assert_phase, instructions.AssertPhaseInstruction)
        TestCase.__assert_instruction_class(cleanup_phase, instructions.CleanupPhaseInstruction)
        return tuple.__new__(cls, (anonymous_phase,
                                   setup_phase,
                                   act_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def anonymous_phase(self) -> PhaseContents:
        return self[0]

    @property
    def setup_phase(self) -> PhaseContents:
        return self[1]

    @property
    def act_phase(self) -> PhaseContents:
        return self[2]

    @property
    def assert_phase(self) -> PhaseContents:
        return self[3]

    @property
    def cleanup_phase(self) -> PhaseContents:
        return self[4]

    @staticmethod
    def __assert_instruction_class(phase_contents: PhaseContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.is_instruction:
                assert isinstance(element.instruction, instruction_class)
