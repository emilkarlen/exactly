__author__ = 'emil'

import os
import unittest

from shelltest.phase_instr.parse import SourceError, PlainTestCaseParser
from shelltest.phase_instr import model
from shelltest.phase_instr import line_source, parse, syntax


class InstructionInPhase(model.Instruction):
    def __init__(self,
                 phase_name: str):
        self._phase_name = phase_name

    @property
    def phase_name(self):
        return self._phase_name


def new_instruction_in_phase(source_line: line_source.Line,
                             phase_name: str) -> model.PhaseContentElement:
    return model.new_instruction_element(source_line,
                                         InstructionInPhase(phase_name))


class InstructionParserForPhase(parse.InstructionParser):
    def __init__(self, phase_name: str):
        self._phase_name = phase_name

    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        return model.new_instruction_element(source_line,
                                             InstructionInPhase(self._phase_name))


class InstructionParserThatFails(parse.InstructionParser):
    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        raise SourceError(source_line,
                          'Unconditional failure')


def parser_without_anonymous_phase() -> PlainTestCaseParser:
    configuration = parse.PhaseAndInstructionsConfiguration(
        None,
        parsers_for_named_phases()
    )
    return parse.new_parser_for(configuration)


def parser_with_anonymous_phase() -> PlainTestCaseParser:
    configuration = parse.PhaseAndInstructionsConfiguration(
        InstructionParserForPhase(None),
        parsers_for_named_phases()
    )
    return parse.new_parser_for(configuration)


def parser_for_phase2_that_fails_unconditionally() -> PlainTestCaseParser:
    configuration = parse.PhaseAndInstructionsConfiguration(
        None,
        (parse.ParserForPhase('phase 1',
                              InstructionParserForPhase('phase 1')),
         parse.ParserForPhase('phase 2',
                              InstructionParserThatFails()))
    )
    return parse.new_parser_for(configuration)


def parsers_for_named_phases():
    return (parse.ParserForPhase('phase 1',
                                 InstructionParserForPhase('phase 1')),
            parse.ParserForPhase('phase 2',
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
        self.assertRaises(SourceError,
                          parse.group_by_phase,
                          [
                              (syntax.TYPE_PHASE,
                               line_source.Line(1, '[phase-name-without-closing-bracket'))
                          ])


class TestParsePlainTestCase(unittest.TestCase):
    def test_all_valid_phases_in_order_of_execution_are_accepted_but_empty(self):
        test_case = self._parse_lines(parser_without_anonymous_phase(),
            ['[phase 1]',
             '[phase 2]'])

        self.assertTrue(not test_case.phases,
                        'There should be no phases, since no phase has any lines')

    def test_valid_anonymous_and_named_phase(self):
        actual_document = self._parse_lines(parser_with_anonymous_phase(),
            ['#comment anonymous',
             '',
             'instruction anonymous',
             '[phase 1]',
             '#comment 1',
             'instruction 1'])

        anonymous_instructions = (
            model.new_comment_element(line_source.Line(1, '#comment anonymous')),
            new_instruction_in_phase(line_source.Line(3, 'instruction anonymous'), None)
        )
        phase1_instructions = (
            model.new_comment_element(line_source.Line(5, '#comment 1')),
            new_instruction_in_phase(line_source.Line(6, 'instruction 1'), 'phase 1')
        )
        expected_phase2instructions = {
            None: model.PhaseContents(anonymous_instructions),
            'phase 1': model.PhaseContents(phase1_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_valid_phase_with_comment_and_instruction(self):
        actual_document = self._parse_lines(parser_without_anonymous_phase(),
            ['[phase 1]',
             '#comment',
             'instruction'])

        phase1_instructions = (
            model.new_comment_element(line_source.Line(2, '#comment')),
            new_instruction_in_phase(line_source.Line(3, 'instruction'), 'phase 1')
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_valid_phase_with_fragmented_phases(self):
        actual_document = self._parse_lines(parser_without_anonymous_phase(),
            ['[phase 1]',
             '#comment 1',
             '',
             '[phase 2]',
             'instruction 2',
             '[phase 1]',
             'instruction 1'])

        phase1_instructions = (
            model.new_comment_element(line_source.Line(2, '#comment 1')),
            new_instruction_in_phase(line_source.Line(7, 'instruction 1'),
                                     'phase 1')
        )
        phase2_instructions = (
            new_instruction_in_phase(line_source.Line(5, 'instruction 2'),
                                     'phase 2'),
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions),
            'phase 2': model.PhaseContents(phase2_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_instruction_in_anonymous_phase_should_not_be_allowed_when_there_is_no_anonymous_phase(self):
        self.assertRaises(SourceError,
                          self._parse_lines,
                          parser_without_anonymous_phase(),
                          [
                              'instruction anonymous',
                              '[phase 1]',
                              'instruction 1'
                          ]
                          )

    def test_parse_should_fail_when_instruction_parser_fails(self):
        self.assertRaises(SourceError,
                          self._parse_lines,
                          parser_for_phase2_that_fails_unconditionally(),
                          [
                              '[phase 2]',
                              'instruction 2'
                          ])

    def test_the_instruction_parser_for_the_current_phase_should_be_used(self):
        actual_document = self._parse_lines(parser_for_phase2_that_fails_unconditionally(),
            [
                '[phase 1]',
                'instruction 1'
            ])
        phase1_instructions = (
            new_instruction_in_phase(line_source.Line(2, 'instruction 1'), 'phase 1'),
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def _parse_lines(self,
                     parser: PlainTestCaseParser,
                     lines: list) -> model.Document:
        plain_document = os.linesep.join(lines)
        ptc_source = line_source.new_for_string(plain_document)
        return parser.apply(ptc_source)

    def _check_document(self,
                        expected_document: model.Document,
                        actual_document: model.Document):
        self.assertEqual(len(expected_document.phases),
                         len(actual_document.phases),
                         'Number of phases')
        for phase_name in expected_document.phases:
            expected_instructions = expected_document.elements_for_phase(phase_name)
            self.assertTrue(phase_name in actual_document.phases,
                            'The actual test case contains the expected phase "%s"' % phase_name)
            actual_instructions = actual_document.elements_for_phase(phase_name)
            self._check_equal_instr_app_seq(expected_instructions, actual_instructions)

    def _check_equal_instr_app_seq(self,
                                   expected_instructions: model.PhaseContents,
                                   actual_instructions: model.PhaseContents):
        self.assertEqual(len(expected_instructions.elements),
                         len(actual_instructions.elements),
                         'Number of instructions in the phase')
        for expected_instruction, actual_instruction in zip(expected_instructions.elements,
                                                            actual_instructions.elements):
            self._check_equal_instruction(expected_instruction, actual_instruction)

    def _check_equal_instruction(self,
                                 expected_instruction: model.PhaseContentElement,
                                 actual_instruction: model.PhaseContentElement):
        self.assertEqual(expected_instruction.source_line,
                         actual_instruction.source_line,
                         'Source lines should be equal')
        if expected_instruction.is_comment:
            self.assertTrue(actual_instruction.is_comment)
            self.assertFalse(actual_instruction.is_instruction)
        else:
            self.assertTrue(actual_instruction.is_instruction)
            self.assertEqual(expected_instruction.instruction.__class__,
                             actual_instruction.instruction.__class__, )
            if isinstance(expected_instruction.instruction, InstructionInPhase):
                self.assertIsInstance(actual_instruction.instruction, InstructionInPhase)
                self.assertEqual(expected_instruction.instruction.phase_name,
                                 actual_instruction.instruction.phase_name)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestGroupByPhase))
    ret_val.addTest(unittest.makeSuite(TestParsePlainTestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
