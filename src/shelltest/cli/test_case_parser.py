from shelltest import phases
from shelltest.document import parse
from shelltest.document.line_source import LineSource
from shelltest.test_case import test_case_struct


class Parser:
    def __init__(self,
                 ptc_parser: parse.PlainTestCaseParser):
        self.__ptc_parser = ptc_parser

    def apply(self,
              line_source: LineSource) -> test_case_struct.TestCase:
        raise NotImplementedError()


def new_parser() -> Parser:
    raise NotImplementedError()


anonymous_phase_parser = None
anonymous_phase = parse.ParserForPhase(phases.ANONYMOUS.name,
                                       anonymous_phase_parser)
configuration = parse.PhaseAndInstructionsConfiguration()
