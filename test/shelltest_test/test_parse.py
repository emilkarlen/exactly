__author__ = 'emil'

import os

import unittest

from shelltest import model
from shelltest import parse
from shelltest import syntax
from shelltest import phase
from shelltest import line_source


def empty_parser() -> model.PlainTestCaseParser:
    return parse.new_parser_for(parse.PhaseAndInstructionsConfiguration.empty(phase.ALL))


class TestPhaseIdentifiers(unittest.TestCase):
    def test_all_valid_phases_in_order_of_execution_are_accepted(self):
        all_phase_headers = map(syntax.phase_header, map(phase.Phase.name, phase.ALL))
        all_phases_ptc = os.linesep.join(all_phase_headers)
        all_phases_ptc_line_source = line_source.new_for_string(all_phases_ptc)
        parser = empty_parser()

        test_case = parser.apply(all_phases_ptc_line_source)

        self.assertTrue(test_case.instructions_for_anonymous_phase().is_empty(),
                        'Each phase should have no instructions: anonymous')
        for ph in phase.ALL:
            self.assertTrue(test_case.instructions_for_phase(ph).is_empty(),
                            'Each phase should have no instructions: ' + ph.name())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestPhaseIdentifiers))
    return ret_val


if __name__ == '__main__':
    unittest.main()
