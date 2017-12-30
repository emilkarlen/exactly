import pathlib
import unittest

from exactly_lib.section_document.model import InstructionInfo, Instruction, ElementType
from exactly_lib.section_document.section_element_parser import ParsedInstruction, ParsedNonInstructionElement, \
    ParsedFileInclusionDirective
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.section_document.parse.test_resources import matches_instruction_info
from exactly_lib_test.section_document.test_resources import section_element_parser_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesInstruction),
        unittest.makeSuite(TestMatchesNonInstruction),
    ])


class TestMatchesInstruction(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        instruction = Instruction()
        description = 'the description'
        instruction_info = InstructionInfo(instruction, description)
        actual_element = ParsedInstruction(LINE_SEQUENCE, instruction_info)

        assertion = sut.matches_instruction(equals_line_sequence(LINE_SEQUENCE),
                                            matches_instruction_info(asrt.equals(description),
                                                                     asrt.is_(instruction)))
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual_element)

    def test_not_matches(self):
        # ARRANGE #
        expected_instruction = Instruction()
        expected_description = 'the description'
        instruction_info = InstructionInfo(expected_instruction, expected_description)
        expected_source = LineSequence(1, ('expected',))
        actual_element = ParsedInstruction(expected_source, instruction_info)

        cases = [
            NameAndValue('mismatch on source',
                         sut.matches_instruction(asrt.not_(equals_line_sequence(expected_source)),
                                                 matches_instruction_info(asrt.equals(expected_description),
                                                                          asrt.is_(expected_instruction)))
                         ),
            NameAndValue('mismatch on description',
                         sut.matches_instruction(equals_line_sequence(expected_source),
                                                 matches_instruction_info(asrt.not_(asrt.equals(expected_description)),
                                                                          asrt.is_(expected_instruction)))
                         ),
            NameAndValue('mismatch on instruction',
                         sut.matches_instruction(equals_line_sequence(expected_source),
                                                 matches_instruction_info(asrt.not_(asrt.equals(expected_description)),
                                                                          asrt.not_(asrt.is_(expected_instruction))))
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(nav.value, actual_element)


class TestMatchesNonInstruction(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        element_type = ElementType.COMMENT
        actual_element = ParsedNonInstructionElement(LINE_SEQUENCE, element_type)

        assertion = sut.matches_non_instruction(equals_line_sequence(LINE_SEQUENCE),
                                                asrt.equals(element_type))
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual_element)

    def test_not_matches(self):
        # ARRANGE #
        element_type = ElementType.COMMENT
        actual_element = ParsedNonInstructionElement(LINE_SEQUENCE, element_type)

        cases = [
            NameAndValue('mismatch on source',
                         sut.matches_non_instruction(asrt.not_(equals_line_sequence(LINE_SEQUENCE)),
                                                     asrt.equals(element_type))
                         ),
            NameAndValue('mismatch on element type',
                         sut.matches_non_instruction(equals_line_sequence(LINE_SEQUENCE),
                                                     asrt.not_(asrt.equals(element_type)))
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(nav.value, actual_element)


class TestMatchesFileInclusionDirective(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        files_to_include = [pathlib.Path('file name')]
        actual_element = ParsedFileInclusionDirective(LINE_SEQUENCE, files_to_include)

        assertion = sut.matches_file_inclusion_directive(equals_line_sequence(LINE_SEQUENCE),
                                                         asrt.equals(files_to_include))
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual_element)

    def test_not_matches(self):
        # ARRANGE #
        files_to_include = [pathlib.Path('file name')]
        actual_element = ParsedFileInclusionDirective(LINE_SEQUENCE, files_to_include)

        cases = [
            NameAndValue('mismatch on source',
                         sut.matches_file_inclusion_directive(asrt.not_(equals_line_sequence(LINE_SEQUENCE)),
                                                              asrt.equals(files_to_include))
                         ),
            NameAndValue('mismatch on files to include',
                         sut.matches_file_inclusion_directive(equals_line_sequence(LINE_SEQUENCE),
                                                              asrt.not_(asrt.equals(files_to_include)))
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(nav.value, actual_element)


LINE_SEQUENCE = LineSequence(1, ('first line',))
