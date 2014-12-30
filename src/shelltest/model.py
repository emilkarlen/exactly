__author__ = 'emil'

from shelltest.line_source import LineSource
from shelltest.phase import Phase


class InstructionApplication:
    """
    A parsed application of an Instruction.

    Arguments/values are necessarily not correct.
    Whether or not depends on if they have been validated.
    """
    pass


class InstructionApplicationSequence:
    """
    A sequence/list of InstructionApplication:s.
    """
    def __init__(self, instruction_applications: list):
        self._instruction_applications = instruction_applications

    def is_empty(self) -> bool:
        return self._instruction_applications == []


class Instruction:
    """

    """
    def parse(self, line_immediately_after_instruction_name: str) -> InstructionApplication:
        raise NotImplementedError()


class InstructionSet:
    """
    All instructions that are available for a single step.
    """
    def __init__(self, instructions: dict):
        self._instructions = instructions

    @staticmethod
    def empty():
        return InstructionSet({})

    def lookup(self, instruction_name: str) -> Instruction:
        return self._instructions[instruction_name]


class TestCase:
    """
    The result of parsing a test case file without encountering any errors.
    """
    def instructions_for_anonymous_phase(self) -> InstructionApplicationSequence:
        raise NotImplementedError()

    def instructions_for_phase(self, phase: Phase) -> InstructionApplicationSequence:
        raise NotImplementedError()


class PlainTestCaseParser:
    """
    Base class for parsers that parse a "plain test case"
    (i.e., a test case that do not need pre-processing).
    """
    def apply(self,
              plain_test_case: LineSource) -> TestCase:
        raise NotImplementedError()