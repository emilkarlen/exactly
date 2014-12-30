__author__ = 'emil'

from shelltest import line_source
from shelltest.line_source import LineSource


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


class SourceError(Exception):
    """
    An exceptions related to a line in the test case.
    """

    def __init__(self,
                 line: line_source.Line,
                 message: str):
        self._line = line
        self._message = message


class TestCase:
    """
    The result of parsing a test case file without encountering any errors.
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


class PlainTestCaseParser:
    """
    Base class for parsers that parse a "plain test case"
    (i.e., a test case that do not need pre-processing).
    """

    def apply(self,
              plain_test_case: LineSource) -> TestCase:
        """
        :raises SourceError The test case cannot be parsed.
        """
        raise NotImplementedError()
