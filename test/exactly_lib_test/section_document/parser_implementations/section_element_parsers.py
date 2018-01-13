import pathlib
import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import section_element_parsers as sut
from exactly_lib.util import line_source
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.section_document.test_resources.document_assertions import equals_empty_element, \
    equals_comment_element, matches_instruction
from exactly_lib_test.section_document.test_resources.section_contents_elements import matches_instruction_info
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestStandardSyntaxElementParser)


class TestStandardSyntaxElementParser(unittest.TestCase):
    def test_parse_empty_line(self):
        parser = sut.StandardSyntaxElementParser(_InstructionParserForInstructionLineThatStartsWith('I'))
        test_cases = [([' '], ''),
                      (['  \t  '], ''),
                      (['  ', 'remaining'], 'remaining'),
                      ]
        for source_lines, remaining_source in test_cases:
            with self.subTest(source_lines=source_lines,
                              remaining_source=remaining_source):
                # ARRANGE #
                source = _source_for_lines(source_lines)
                # ACT #
                element = parser.parse(pathlib.Path(), source)
                # ASSERT #
                element_assertion = equals_empty_element(LineSequence(1, (source_lines[0],)))
                element_assertion.apply_with_message(self, element, 'element')
                self.assertEqual('\n'.join(source_lines[1:]),
                                 source.remaining_source,
                                 'Remaining source')

    def test_parse_comment_line(self):
        parser = sut.StandardSyntaxElementParser(_InstructionParserForInstructionLineThatStartsWith('I'))
        test_cases = [(['# comment'], ''),
                      (['  #  comment'], ''),
                      (['#   ', 'remaining'], 'remaining'),
                      ]
        for source_lines, remaining_source in test_cases:
            with self.subTest(source_lines=source_lines,
                              remaining_source=remaining_source):
                # ARRANGE #
                source = _source_for_lines(source_lines)
                # ACT #
                element = parser.parse(pathlib.Path(), source)
                # ASSERT #
                element_assertion = equals_comment_element(LineSequence(1, (source_lines[0],)))
                element_assertion.apply_with_message(self, element, 'element')
                self.assertEqual(remaining_source,
                                 source.remaining_source,
                                 'Remaining source')

    def test_parse_single_line_instruction(self):
        parser = sut.StandardSyntaxElementParser(_InstructionParserForInstructionLineThatStartsWith('I'))
        test_cases = [(['I arguments'], ''),
                      (['I arguments', 'remaining'], 'remaining'),
                      (['I line 1', 'I line 2', 'not an instruction'], 'not an instruction'),
                      ]
        for source_lines, remaining_source in test_cases:
            with self.subTest(source_lines=source_lines,
                              remaining_source=remaining_source):
                source = _source_for_lines(source_lines)
                # ACT #
                element = parser.parse(pathlib.Path(), source)
                # ASSERT #
                expected_instruction_source = LineSequence(1, (source_lines[0],))
                element_assertion = matches_instruction(
                    source=equals_line_sequence(expected_instruction_source),
                    instruction_info=matches_instruction_info(
                        assertion_on_description=asrt.is_none,
                        assertion_on_instruction=asrt.is_instance(Instruction)))
                element_assertion.apply_with_message(self, element, 'element')
                self.assertEqual(remaining_source,
                                 source.remaining_source,
                                 'Remaining source')

    def test_element_from_instruction_parser_SHOULD_be_assigned_to_section_contents_element(self):
        expected_instruction_info = InstructionInfo(Instruction(),
                                                    'description')
        expected = sut.ParsedInstruction(line_source.LineSequence(1,
                                                                  ('first line text',)),
                                         expected_instruction_info)
        parser = sut.StandardSyntaxElementParser(_InstructionParserThatGivesConstant(expected))
        source = _source_for_lines(['ignored', 'source', 'lines'])
        # ACT #
        element = parser.parse(pathlib.Path(), source)
        # ASSERT #
        element_assertion = matches_instruction(
            source=asrt.is_(expected.source),
            instruction_info=matches_instruction_info(
                assertion_on_description=asrt.is_(expected_instruction_info.description),
                assertion_on_instruction=asrt.is_(expected_instruction_info.instruction)))
        element_assertion.apply_with_message(self, element, 'element')


class _InstructionParserForInstructionLineThatStartsWith(sut.InstructionAndDescriptionParser):
    def __init__(self, instruction_line_identifier: str):
        self.instruction_line_identifier = instruction_line_identifier

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> sut.ParsedInstruction:
        first_line_number = source.current_line_number
        dummy_source = line_source.LineSequence(first_line_number, (source.current_line_text,))
        is_instruction = False
        while not source.is_at_eof and source.current_line_text.startswith(self.instruction_line_identifier):
            source.consume_current_line()
            is_instruction = True
        if not is_instruction:
            raise ValueError('Not an instruction')
        return sut.ParsedInstruction(dummy_source,
                                     InstructionInfo(Instruction(), None))


class _InstructionParserThatGivesConstant(sut.InstructionAndDescriptionParser):
    def __init__(self, return_value: sut.ParsedInstruction):
        self.return_value = return_value

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> sut.ParsedInstruction:
        return self.return_value


class Instruction(model.Instruction):
    pass


def _source_for_lines(source_lines: list) -> ParseSource:
    source_string = '\n'.join(source_lines)
    return ParseSource(source_string)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
