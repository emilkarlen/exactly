from shelltest import phases
from shelltest.document import model
from shelltest.document import parse
from shelltest.document.parse import InstructionParser, SourceError, ParserForPhase
from shelltest.general import line_source
from shelltest.general.line_source import LineSource
from shelltest.test_case import test_case_struct


class Parser:
    def __init__(self,
                 ptc_parser: parse.PlainTestCaseParser):
        self.__ptc_parser = ptc_parser

    def apply(self,
              plain_test_case: LineSource) -> test_case_struct.TestCase:
        document = self.__ptc_parser.apply(plain_test_case)
        return test_case_struct.TestCase(
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ANONYMOUS.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.SETUP.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ACT.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ASSERT.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.CLEANUP.name),
        )


def new_parser() -> Parser:
    failing_parser = InstructionParserThatFailsUnconditionally()
    anonymous_phase = parse.ParserForPhase(phases.ANONYMOUS.name,
                                           failing_parser)
    configuration = parse.PhaseAndInstructionsConfiguration(
        anonymous_phase,
        (
            ParserForPhase(phases.SETUP.name,
                           failing_parser),
            ParserForPhase(phases.ACT.name,
                           failing_parser),
            ParserForPhase(phases.ASSERT.name,
                           failing_parser),
            ParserForPhase(phases.CLEANUP.name,
                           failing_parser),
        )
    )
    return Parser(parse.new_parser_for(configuration))


class InstructionParserThatFailsUnconditionally(InstructionParser):
    def apply(self, line: line_source.Line) -> model.PhaseContentElement:
        raise SourceError(line, 'This parser fails unconditionally')


