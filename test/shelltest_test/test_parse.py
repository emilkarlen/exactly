__author__ = 'emil'

import os

import unittest

from shelltest import model
from shelltest import parse
from shelltest import syntax
from shelltest import phase
from shelltest import line_source


class InstructionApplicationForPhase(model.InstructionApplication):
    def __init__(self,
                 source_line: line_source.Line,
                 phase_name: str):
        model.InstructionApplication.__init__(self, source_line)
        self._phase_name = phase_name

    def phase_name(self):
        return self._phase_name


class InstructionParserForPhase(parse.InstructionParser):
    def __init__(self, phase_name: str):
        self._phase_name = phase_name

    def apply(self, source_line: line_source.Line) -> model.InstructionApplication:
        return InstructionApplicationForPhase(source_line,
                                              self._phase_name)


def parser_without_anonymous_phase() -> model.PlainTestCaseParser:
    configuration = parse.PhaseAndInstructionsConfiguration(
        None,
        parsers_for_named_phases()
    )
    return parse.new_parser_for(configuration)


def parser_with_anonymous_phase() -> model.PlainTestCaseParser:
    configuration = parse.PhaseAndInstructionsConfiguration(
        InstructionParserForPhase(None),
        parsers_for_named_phases()
    )
    return parse.new_parser_for(configuration)


def parsers_for_named_phases():
    return (parse.ParserForPhase(phase.Phase('phase 1'),
                                 InstructionParserForPhase('phase 1')),
            parse.ParserForPhase(phase.Phase('phase 2'),
                                 InstructionParserForPhase('phase 2')))


class TestGroupByPhase(unittest.TestCase):
    def test_valid(self):
        lines_for_anonymous = [
            (syntax.TYPE_INSTRUCTION, line_source.Line(1, 'i0/1'))
        ]

        phase1_line = line_source.Line(20, '[phase 1]')
        lines_for_phase1 = [
            (syntax.TYPE_INSTRUCTION, line_source.Line(1, 'i1/1')),
            (syntax.TYPE_COMMENT, line_source.Line(2, '#1')),
            (syntax.TYPE_INSTRUCTION, line_source.Line(3, 'i1/2')),
        ]

        phase2_line = line_source.Line(30, '[phase 2]')
        lines_for_phase2 = [
        ]

        phase3_line = line_source.Line(40, '[phase 3]')
        lines_for_phase3 = [
            (syntax.TYPE_INSTRUCTION, line_source.Line(1, 'i3/1')),
            (syntax.TYPE_COMMENT, line_source.Line(2, '#3')),
        ]

        lines = lines_for_anonymous + \
                [(syntax.TYPE_PHASE, phase1_line)] + \
                lines_for_phase1 + \
                [(syntax.TYPE_PHASE, phase2_line)] + \
                lines_for_phase2 + \
                [(syntax.TYPE_PHASE, phase3_line)] + \
                lines_for_phase3

        expected = [
            parse.PhaseWithLines(None,
                                 None,
                                 tuple(lines_for_anonymous)),
            parse.PhaseWithLines('phase 1',
                                 phase1_line,
                                 tuple(lines_for_phase1)),
            parse.PhaseWithLines('phase 2',
                                 phase2_line,
                                 tuple(lines_for_phase2)),
            parse.PhaseWithLines('phase 3',
                                 phase3_line,
                                 tuple(lines_for_phase3)),
        ]

        actual = parse.group_by_phase(lines)
        self.assertEqual(expected, actual)

    def test_lines_in_anonymous_phase_should_not_be_required(self):
        phase1_line = line_source.Line(20, '[phase 1]')
        lines_for_phase1 = [
            (syntax.TYPE_INSTRUCTION, line_source.Line(1, 'i1/1')),
        ]
        lines = [(syntax.TYPE_PHASE, phase1_line)] + \
                lines_for_phase1

        expected = [
            parse.PhaseWithLines('phase 1',
                                 phase1_line,
                                 tuple(lines_for_phase1)),
        ]

        actual = parse.group_by_phase(lines)
        self.assertEqual(expected, actual)

    def test_invalid_phase_name_should_raise_exception(self):
        self.assertRaises(model.SourceError,
                          parse.group_by_phase,
                          [(syntax.TYPE_PHASE, line_source.Line(1, '[phase-name-without-closing-bracket'))])


class TestParsePlainTestCase(unittest.TestCase):

    def test_all_valid_phases_in_order_of_execution_are_accepted_but_empty(self):
        all_phases_ptc = os.linesep.join(['[phase 1]',
                                          '[phase 2]'])
        all_phases_ptc_line_source = line_source.new_for_string(all_phases_ptc)
        parser = parser_without_anonymous_phase()

        test_case = parser.apply(all_phases_ptc_line_source)

        self.assertTrue(not test_case.phases(),
                        'There should be no phases, since no phase has any lines')

    def test_valid_anonymous_and_named_phase(self):
        actual_test_case = self._parse_lines_without_anonymous_phase(parser_with_anonymous_phase(),
                                                                     ['#comment anonymous',
                                                                      '',
                                                                      'instruction anonymous',
                                                                      '[phase 1]',
                                                                      '#comment 1',
                                                                      'instruction 1'])

        anonymous_instructions = (
            parse.InstructionForComment(line_source.Line(1, '#comment anonymous')),
            InstructionApplicationForPhase(line_source.Line(3, 'instruction anonymous'), None)
        )
        phase1_instructions = (
            parse.InstructionForComment(line_source.Line(5, '#comment 1')),
            InstructionApplicationForPhase(line_source.Line(6, 'instruction 1'), 'phase 1')
        )
        expected_phase2instructions = {
            None: model.InstructionApplicationSequence(anonymous_instructions),
            'phase 1': model.InstructionApplicationSequence(phase1_instructions)
        }
        expected_test_case = model.TestCase(expected_phase2instructions)
        self._check_test_case(expected_test_case, actual_test_case)

    def test_valid_phase_with_comment_and_instruction(self):
        actual_test_case = self._parse_lines_without_anonymous_phase(parser_without_anonymous_phase(),
                                                                     ['[phase 1]',
                                                                      '#comment',
                                                                      'instruction'])

        phase1_instructions = (
            parse.InstructionForComment(line_source.Line(2, '#comment')),
            InstructionApplicationForPhase(line_source.Line(3, 'instruction'), 'phase 1')
        )
        expected_phase2instructions = {
            'phase 1': model.InstructionApplicationSequence(phase1_instructions)
        }
        expected_test_case = model.TestCase(expected_phase2instructions)
        self._check_test_case(expected_test_case, actual_test_case)

    def test_valid_phase_with_fragmented_phases(self):
        actual_test_case = self._parse_lines_without_anonymous_phase(parser_without_anonymous_phase(),
                                                                     ['[phase 1]',
                                                                      '#comment 1',
                                                                      '',
                                                                      '[phase 2]',
                                                                      'instruction 2',
                                                                      '[phase 1]',
                                                                      'instruction 1'])

        phase1_instructions = (
            parse.InstructionForComment(line_source.Line(2, '#comment 1')),
            InstructionApplicationForPhase(line_source.Line(7, 'instruction 1'),
                                           'phase 1')
        )
        phase2_instructions = (
            InstructionApplicationForPhase(line_source.Line(5, 'instruction 2'),
                                           'phase 2'),
        )
        expected_phase2instructions = {
            'phase 1': model.InstructionApplicationSequence(phase1_instructions),
            'phase 2': model.InstructionApplicationSequence(phase2_instructions)
        }
        expected_test_case = model.TestCase(expected_phase2instructions)
        self._check_test_case(expected_test_case, actual_test_case)

    def _parse_lines_without_anonymous_phase(self,
                                             parser: model.PlainTestCaseParser,
                                             lines: list) -> model.TestCase:
        plain_test_case = os.linesep.join(lines)
        ptc_source = line_source.new_for_string(plain_test_case)
        return parser.apply(ptc_source)

    def _check_test_case(self,
                         expected_test_case: model.TestCase,
                         actual_test_case: model.TestCase):
        self.assertEqual(len(expected_test_case.phases()),
                         len(actual_test_case.phases()),
                         'Number of phases')
        for phase_name in expected_test_case.phases():
            expected_instructions = expected_test_case.instructions_for_phase(phase_name)
            self.assertTrue(phase_name in actual_test_case.phases(),
                            'The actual test case contains the expected phase "%s"' % phase_name)
            actual_instructions = actual_test_case.instructions_for_phase(phase_name)
            self._check_equal_instr_app_seq(expected_instructions, actual_instructions)

    def _check_equal_instr_app_seq(self,
                                   expected_instructions: model.InstructionApplicationSequence,
                                   actual_instructions: model.InstructionApplicationSequence):
        self.assertEqual(len(expected_instructions.instruction_applications()),
                         len(actual_instructions.instruction_applications()),
                         'Number of instructions in the phase')
        for expected_instruction, actual_instruction in zip(expected_instructions.instruction_applications(),
                                                            actual_instructions.instruction_applications()):
            self._check_equal_instruction(expected_instruction, actual_instruction)

    def _check_equal_instruction(self,
                                 expected_instruction: model.InstructionApplication,
                                 actual_instruction: model.InstructionApplication):
        self.assertEqual(expected_instruction.source_line(),
                         actual_instruction.source_line(),
                         'Source lines should be equal')
        if isinstance(expected_instruction, parse.InstructionForComment):
            self.assertTrue(isinstance(actual_instruction, parse.InstructionForComment),
                            'Expected comment. Got ' + str(actual_instruction))
        elif isinstance(expected_instruction, InstructionApplicationForPhase):
            self.assertTrue(isinstance(actual_instruction, InstructionApplicationForPhase))
            self.assertEqual(expected_instruction.phase_name(),
                             actual_instruction.phase_name(),
                             'Phase name should be equal')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestGroupByPhase))
    ret_val.addTest(unittest.makeSuite(TestParsePlainTestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
