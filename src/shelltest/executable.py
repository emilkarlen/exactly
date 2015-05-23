import argparse

from shelltest import phases
from shelltest.document import parse


anonymous_phase_parser = parse.
anonymous_phase = parse.ParserForPhase(phases.ANONYMOUS.name,
                                       anonymous_phase_parser)
configuration = parse.PhaseAndInstructionsConfiguration()

parser = argparse.ArgumentParser(description='Execute Shelltest test case')
parser.add_argument('file',
                    type=str,
                    help='The file containing the test case')

args = parser.parse_args()
