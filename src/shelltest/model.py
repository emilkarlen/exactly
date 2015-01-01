__author__ = 'emil'

from shelltest import line_source


class Instruction:
    """
    Base class for a parsed instruction line.

    Arguments/values are necessarily not correct.
    Whether or not depends on if they have been validated.
    """

    def __init__(self, source_line: line_source.Line):
        self._source_line = source_line

    def source_line(self) -> line_source.Line:
        return self._source_line


class InstructionSequence:
    """
    A sequence/list of Instruction:s.
    """

    def __init__(self, instructions: tuple):
        self._instructions = instructions

    def is_empty(self) -> bool:
        return not self._instructions

    def instructions(self):
        return self._instructions


class Document:
    """
    The result of parsing a file without encountering any errors.
    """

    def __init__(self, phase2instructions: dict):
        """
        :param phase2instructions dictionary str -> InstructionApplicationSequence
        """
        self._phase2instructions = phase2instructions

    def phases(self) -> frozenset:
        return self._phase2instructions.keys()

    def instructions_for_phase(self, phase_name: str) -> InstructionSequence:
        return self._phase2instructions[phase_name]


