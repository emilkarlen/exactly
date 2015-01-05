__author__ = 'emil'

from shelltest.phase_instr import line_source


class Instruction:
    """
    Base class for a parsed instruction line.

    Arguments/values are necessarily not correct.
    Whether or not depends on if they have been validated.
    """

    def __init__(self, source_line: line_source.Line):
        self._source_line = source_line

    @property
    def source_line(self) -> line_source.Line:
        return self._source_line

    def execute(self, phase_name: str, global_environment, phase_environment):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class InstructionSequence:
    """
    A sequence/list of Instruction:s.
    """

    def __init__(self, instructions: tuple):
        """
        :param instructions: List of Instruction.
        """
        self._instructions = instructions

    @property
    def instructions(self) -> tuple:
        return self._instructions


class Document:
    """
    The result of parsing a file without encountering any errors.
    """

    def __init__(self, phase2instructions: dict):
        """
        :param phase2instructions dictionary str -> InstructionSequence
        """
        self._phase2instructions = phase2instructions

    @property
    def phases(self) -> frozenset:
        return self._phase2instructions.keys()

    def instructions_for_phase(self, phase_name: str) -> InstructionSequence:
        return self._phase2instructions[phase_name]

    def execute(self, global_environment, phases: iter):
        """
        Executes the given phases in the given order.
        :param global_environment: An environment passed to every Instruction.
        :param phases: [(phase_name: str, phase_environment)]
        List of phases to execute, and the environment to use for each phase.
        The phases are executed in the order they appear in the list (a phase may be executed more than
        one time). Phases that have no counterpart in the Document are silently ignored.
        :return:
        """
        for phase_name, phase_environment in phases:
            if phase_name in self._phase2instructions:
                instruction_sequence = self._phase2instructions[phase_name]
                for instruction in instruction_sequence.instructions:
                    assert isinstance(instruction, Instruction)
                    instruction.execute(phase_name, global_environment, phase_environment)