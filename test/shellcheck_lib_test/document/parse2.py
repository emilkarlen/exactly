import os
import unittest

from shellcheck_lib.document.parse2 import SourceError, PlainDocumentParser
from shellcheck_lib.document import model
from shellcheck_lib.document import parse2
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import Line
from shellcheck_lib_test.document.test_resources import assert_equals_line, assert_equals_line_sequence
from shellcheck_lib_test.util.assert_utils import TestCaseWithMessageHeader, \
    MessageWithHeaderConstructor

_COMMENT_START = 'COMMENT'

_MULTI_LINE_INSTRUCTION_LINE_START = 'MULTI-LINE-INSTRUCTION'


def is_multi_line_instruction_line(line: str) -> bool:
    return line[:len(_MULTI_LINE_INSTRUCTION_LINE_START)] == _MULTI_LINE_INSTRUCTION_LINE_START


def is_comment_line(line: str) -> bool:
    return line[:len(_COMMENT_START)] == _COMMENT_START


class InstructionInSection(model.Instruction):
    def __init__(self,
                 section_name: str):
        self._section_name = section_name

    @property
    def phase_name(self):
        return self._section_name


def new_instruction(line_number: int,
                    line_text: str,
                    phase_name: str) -> model.PhaseContentElement:
    return model.new_instruction_e(line_source.LineSequence(line_number,
                                                            (line_text,)),
                                   InstructionInSection(phase_name))


def new_instruction__multi_line(line_number: int,
                                lines: list,
                                phase_name: str) -> model.PhaseContentElement:
    return model.new_instruction_e(line_source.LineSequence(line_number,
                                                            tuple(lines)),
                                   InstructionInSection(phase_name))


def new_comment(line_number: int,
                line_text: str) -> model.PhaseContentElement:
    return model.new_comment_e(line_source.LineSequence(line_number,
                                                        (line_text,)))


def new_empty(line_number: int,
              line_text: str) -> model.PhaseContentElement:
    return model.new_empty_e(line_source.LineSequence(line_number,
                                                      (line_text,)))


class InstructionParserForPhase(parse2.SectionElementParser):
    def __init__(self, section_name: str):
        self._section_name = section_name

    def apply(self, source: line_source.LineSequenceBuilder) -> model.PhaseContentElement:
        the_line = source.lines[0]
        if the_line == '':
            return model.new_empty_e(source.build())
        if is_comment_line(the_line):
            return model.new_comment_e(source.build())
        if is_multi_line_instruction_line(the_line):
            # Eat additional lines
            while source.has_next():
                next_line = source.next_line()
                if not is_multi_line_instruction_line(next_line):
                    source.return_line()
                    break
            return model.new_instruction_e(source.build(),
                                           InstructionInSection(self._section_name))
        return model.new_instruction_e(source.build(),
                                       InstructionInSection(self._section_name))


class InstructionParserThatFails(parse2.SectionElementParser):
    def apply(self, source: line_source.LineSequenceBuilder) -> model.PhaseContentElement:
        raise SourceError(source.build().first_line,
                          'Unconditional failure')


def parser_without_anonymous_phase() -> PlainDocumentParser:
    configuration = parse2.SectionsConfiguration(
        None,
        parsers_for_named_phases()
    )
    return parse2.new_parser_for(configuration)


def parser_with_anonymous_phase() -> PlainDocumentParser:
    configuration = parse2.SectionsConfiguration(
        InstructionParserForPhase(None),
        parsers_for_named_phases()
    )
    return parse2.new_parser_for(configuration)


def parser_for_phase2_that_fails_unconditionally() -> PlainDocumentParser:
    configuration = parse2.SectionsConfiguration(
        None,
        (parse2.SectionConfiguration('phase 1',
                                     InstructionParserForPhase('phase 1')),
         parse2.SectionConfiguration('phase 2',
                                     InstructionParserThatFails()))
    )
    return parse2.new_parser_for(configuration)


def parsers_for_named_phases():
    return (parse2.SectionConfiguration('phase 1',
                                        InstructionParserForPhase('phase 1')),
            parse2.SectionConfiguration('phase 2',
                                        InstructionParserForPhase('phase 2')))


# class TestGroupByPhase(unittest.TestCase):
#     def test_valid(self):
#         lines_for_anonymous = [
#             (syntax.TYPE_INSTRUCTION, Line(1, 'i0/1'))
#         ]
#
#         phase1_line = Line(20, '[phase 1]')
#         lines_for_phase1 = [
#             (syntax.TYPE_INSTRUCTION, Line(1, 'i1/1')),
#             (syntax.TYPE_COMMENT, Line(2, '#1')),
#             (syntax.TYPE_INSTRUCTION, Line(3, 'i1/2')),
#         ]
#
#         phase2_line = Line(30, '[phase 2]')
#         lines_for_phase2 = [
#         ]
#
#         phase3_line = Line(40, '[phase 3]')
#         lines_for_phase3 = [
#             (syntax.TYPE_INSTRUCTION, Line(1, 'i3/1')),
#             (syntax.TYPE_COMMENT, Line(2, '#3')),
#         ]
#
#         lines = lines_for_anonymous + \
#                 [(syntax.TYPE_PHASE, phase1_line)] + \
#                 lines_for_phase1 + \
#                 [(syntax.TYPE_PHASE, phase2_line)] + \
#                 lines_for_phase2 + \
#                 [(syntax.TYPE_PHASE, phase3_line)] + \
#                 lines_for_phase3
#
#         expected = [
#             parse2.PhaseWithLines(None,
#                                   None,
#                                   tuple(lines_for_anonymous)),
#             parse2.PhaseWithLines('phase 1',
#                                   phase1_line,
#                                   tuple(lines_for_phase1)),
#             parse2.PhaseWithLines('phase 2',
#                                   phase2_line,
#                                   tuple(lines_for_phase2)),
#             parse2.PhaseWithLines('phase 3',
#                                   phase3_line,
#                                   tuple(lines_for_phase3)),
#         ]
#
#         actual = parse2.group_by_phase(lines)
#         self.assertEqual(expected, actual)
#
#     def test_lines_in_anonymous_phase_should_not_be_required(self):
#         phase1_line = Line(20, '[phase 1]')
#         lines_for_phase1 = [
#             (syntax.TYPE_INSTRUCTION, Line(1, 'i1/1')),
#         ]
#         lines = [(syntax.TYPE_PHASE, phase1_line)] + \
#                 lines_for_phase1
#
#         expected = [
#             parse2.PhaseWithLines('phase 1',
#                                   phase1_line,
#                                   tuple(lines_for_phase1)),
#         ]
#
#         actual = parse2.group_by_phase(lines)
#         self.assertEqual(expected, actual)
#
#     def test_invalid_phase_name_should_raise_exception(self):
#         self.assertRaises(SourceError,
#                           parse2.group_by_phase,
#                           [
#                               (syntax.TYPE_PHASE,
#                                Line(1, '[phase-name-without-closing-bracket'))
#                           ])


class ParseTestBase(unittest.TestCase):
    def _parse_lines(self,
                     parser: PlainDocumentParser,
                     lines: list) -> model.Document:
        plain_document = os.linesep.join(lines) + os.linesep
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
            actual_elements = actual_document.elements_for_phase(phase_name)
            ElementChecker(self, phase_name).check_equal_phase_contents(expected_instructions,
                                                                        actual_elements)


class TestParseSingleLineElements(ParseTestBase):
    def test_phases_without_elements_are_registered(self):
        actual_document = self._parse_lines(parser_without_anonymous_phase(),
                                            ['[phase 1]',
                                             '[phase 2]'])

        expected_phase2instructions = {
            'phase 1': model.PhaseContents(()),
            'phase 2': model.PhaseContents(()),
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_initial_empty_lines_and_comment_lines_should_be_ignored_when_there_is_no_anonymous_phase(self):
        actual_document = self._parse_lines(parser_without_anonymous_phase(),
                                            ['# standard-comment anonymous',
                                             '',
                                             '[phase 1]',
                                             'COMMENT 1',
                                             '',
                                             'instruction 1'])

        phase1_instructions = (
            new_comment(4, 'COMMENT 1'),
            new_empty(5, ''),
            new_instruction(6, 'instruction 1', 'phase 1')
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions),
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_valid_anonymous_and_named_phase(self):
        actual_document = self._parse_lines(parser_with_anonymous_phase(),
                                            ['COMMENT anonymous',
                                             '',
                                             'instruction anonymous',
                                             '[phase 1]',
                                             'COMMENT 1',
                                             'instruction 1'])

        anonymous_instructions = (
            new_comment(1, 'COMMENT anonymous'),
            new_empty(2, ''),
            new_instruction(3, 'instruction anonymous', None)
        )
        phase1_instructions = (
            new_comment(5, 'COMMENT 1'),
            new_instruction(6, 'instruction 1', 'phase 1')
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
                                             'COMMENT',
                                             'instruction'])

        phase1_instructions = (
            new_comment(2, 'COMMENT'),
            new_instruction(3, 'instruction', 'phase 1')
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_valid_phase_with_fragmented_phases(self):
        actual_document = self._parse_lines(parser_without_anonymous_phase(),
                                            ['[phase 1]',
                                             'COMMENT 1',
                                             '',
                                             '[phase 2]',
                                             'instruction 2',
                                             '[phase 1]',
                                             'instruction 1'])

        phase1_instructions = (
            new_comment(2, 'COMMENT 1'),
            new_empty(3, ''),
            new_instruction(7, 'instruction 1',
                            'phase 1')
        )
        phase2_instructions = (
            new_instruction(5, 'instruction 2',
                            'phase 2'),
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions),
            'phase 2': model.PhaseContents(phase2_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_instruction_in_anonymous_phase_should_not_be_allowed_when_there_is_no_anonymous_phase(self):
        with self.assertRaises(SourceError) as cm:
            doc = self._parse_lines(
                parser_without_anonymous_phase(),
                [
                    'instruction anonymous',
                    '[phase 1]',
                    'instruction 1'
                ])
        assert_equals_line(self,
                           Line(1, 'instruction anonymous'),
                           cm.exception.line)

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
            new_instruction(2, 'instruction 1',
                            'phase 1'),
        )
        expected_phase2instructions = {
            'phase 1': model.PhaseContents(phase1_instructions)
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)


class TestParseMultiLineElements(ParseTestBase):
    def test_single_multi_line_instruction_that_is_actually_only_a_single_line_in_anonymous_phase(self):
        actual_document = self._parse_lines(parser_with_anonymous_phase(),
                                            ['MULTI-LINE-INSTRUCTION 1'])

        anonymous_phase_instructions = (
            new_instruction(1, 'MULTI-LINE-INSTRUCTION 1', None),
        )
        expected_phase2instructions = {
            None: model.PhaseContents(anonymous_phase_instructions),
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_single_multi_line_instruction_in_anonymous_phase_that_occupies_whole_doc(self):
        actual_document = self._parse_lines(parser_with_anonymous_phase(),
                                            ['MULTI-LINE-INSTRUCTION 1',
                                             'MULTI-LINE-INSTRUCTION 2'])

        anonymous_phase_instructions = (
            new_instruction__multi_line(1,
                                        ['MULTI-LINE-INSTRUCTION 1',
                                         'MULTI-LINE-INSTRUCTION 2'],
                                        None),
        )
        expected_phase2instructions = {
            None: model.PhaseContents(anonymous_phase_instructions),
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_single_multi_line_instruction_in_anonymous_phase_surrounded_by_empty_lines(self):
        actual_document = self._parse_lines(parser_with_anonymous_phase(),
                                            ['',
                                             'MULTI-LINE-INSTRUCTION 1',
                                             'MULTI-LINE-INSTRUCTION 2',
                                             ''])

        anonymous_phase_instructions = (
            new_empty(1, ''),
            new_instruction__multi_line(2,
                                        ['MULTI-LINE-INSTRUCTION 1',
                                         'MULTI-LINE-INSTRUCTION 2'],
                                        None),
            new_empty(4, ''),
        )
        expected_phase2instructions = {
            None: model.PhaseContents(anonymous_phase_instructions),
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)

    def test_single_multi_line_instruction_in_anonymous_phase_ended_by_section_header(self):
        actual_document = self._parse_lines(parser_with_anonymous_phase(),
                                            ['',
                                             'MULTI-LINE-INSTRUCTION 1',
                                             'MULTI-LINE-INSTRUCTION 2',
                                             '[phase 1]',
                                             'instruction 1'])

        anonymous_phase_instructions = (
            new_empty(1, ''),
            new_instruction__multi_line(2,
                                        ['MULTI-LINE-INSTRUCTION 1',
                                         'MULTI-LINE-INSTRUCTION 2'],
                                        None),
        )
        phase1_instructions = (
            new_instruction(5, 'instruction 1',
                            'phase 1'),
        )
        expected_phase2instructions = {
            None: model.PhaseContents(anonymous_phase_instructions),
            'phase 1': model.PhaseContents(phase1_instructions),
        }
        expected_document = model.Document(expected_phase2instructions)
        self._check_document(expected_document, actual_document)


class ElementChecker(TestCaseWithMessageHeader):
    def __init__(self,
                 test_case: unittest.TestCase,
                 phase_name: str):
        super().__init__(test_case,
                         MessageWithHeaderConstructor('Phase "%s"' % phase_name))

    def check_equal_phase_contents(self,
                                   expected_elements: model.PhaseContents,
                                   actual_elements: model.PhaseContents):
        self.tc.assertEqual(len(expected_elements.elements),
                            len(actual_elements.elements),
                            self.msg('Number of elements in the phase'))
        for expected_element, actual_element in zip(expected_elements.elements,
                                                    actual_elements.elements):
            self.check_equal_element(expected_element, actual_element)

    def check_equal_element(self,
                            expected_element: model.PhaseContentElement,
                            actual_element: model.PhaseContentElement):
        self.tc.assertEqual(expected_element.element_type,
                            actual_element.element_type,
                            self.msg('Element type'))
        assert_equals_line_sequence(self.tc,
                                    expected_element.source,
                                    actual_element.source,
                                    self.message_header)
        # self.tc.assertEqual(expected_element.source_line,
        #                     actual_element.source_line,
        #                     self.msg('Source lines should be equal'))
        if expected_element.is_comment:
            self.tc.assertTrue(actual_element.is_comment)
            self.tc.assertFalse(actual_element.is_instruction)
        else:
            self.tc.assertTrue(actual_element.is_instruction)
            self.tc.assertEqual(expected_element.instruction.__class__,
                                actual_element.instruction.__class__, )
            if isinstance(expected_element.instruction, InstructionInSection):
                self.tc.assertIsInstance(actual_element.instruction, InstructionInSection)
                self.tc.assertEqual(expected_element.instruction.phase_name,
                                    actual_element.instruction.phase_name,
                                    self.msg('Recorded phase name of instruction'))


def suite():
    ret_val = unittest.TestSuite()
    # ret_val.addTest(unittest.makeSuite(TestGroupByPhase))
    ret_val.addTest(unittest.makeSuite(TestParseSingleLineElements))
    ret_val.addTest(unittest.makeSuite(TestParseMultiLineElements))
    return ret_val


if __name__ == '__main__':
    unittest.main()
