__author__ = 'emil'

from shelltest.phase import Phase
from shelltest import model
from shelltest.model import InstructionSet
from shelltest import line_source


class StepsAndInstructionsWithArgument:
    """

    """
    pass


class PhaseAndInstructionsConfiguration:
    """
    Phases and their available instructions.
    """
    def __init__(self,
                 instructions_for_anonymous_phase: InstructionSet,
                 instructions_for_named_phase: dict):
        self._instructions_for_anonymous_phase = instructions_for_anonymous_phase
        self._instructions_for_named_phase = instructions_for_named_phase

    @staticmethod
    def empty(phases: list):
        phase_configs = {}
        for phase in phases:
            phase_configs[phase.name()] = InstructionSet.empty()
        return PhaseAndInstructionsConfiguration(InstructionSet.empty(), phase_configs)

    def instructions_for_anonymous_phase(self) -> InstructionSet:
        """
        :return: Not None
        """
        return self._instructions_for_anonymous_phase

    def instructions_for_named_phase(self, phase: Phase) -> InstructionSet:
        """
        :return: Not None
        """
        try:
            return self._instructions_for_named_phase[phase.name()]
        except KeyError:
            return InstructionSet.empty()


class PlainTestCaseParserForPhaseAndInstructionsConfiguration(model.PlainTestCaseParser):
    def __init__(self, configuration: PhaseAndInstructionsConfiguration):
        self._configuration = configuration

    def apply(self, plain_test_case: line_source.LineSource) -> model.TestCase:
        raise NotImplementedError()


def new_parser_for(configuration: PhaseAndInstructionsConfiguration) -> model.PlainTestCaseParser:
    return PlainTestCaseParserForPhaseAndInstructionsConfiguration(configuration)
