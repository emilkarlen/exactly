import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.parser_implementations import instruction_parsers as sut
from exactly_lib_test.section_document.test_resources.parse_source import source3
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInstructionParserThatConsumesRestOfCurrentLine)


class InstructionParserThatConsumesCurrentLineTestImpl(sut.InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> model.Instruction:
        return Instruction(rest_of_line)


class Instruction(model.Instruction):
    def __init__(self, argument: str):
        self.argument = argument


class TestInstructionParserThatConsumesRestOfCurrentLine(unittest.TestCase):
    parser = InstructionParserThatConsumesCurrentLineTestImpl()

    def runTest(self):
        test_cases = [
            ([''], 0, '',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_false)
             ),
            (['abc'], 0, 'abc',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_false)
             ),
            (['abc'], 1, 'bc',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_false)
             ),
            (['abc', 'def'], 0, 'abc',
             assert_source(is_at_eof=asrt.is_false,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(2),
                           remaining_part_of_current_line=asrt.equals('def'))
             ),
            (['abc', 'def'], 2, 'c',
             assert_source(is_at_eof=asrt.is_false,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(2),
                           remaining_part_of_current_line=asrt.equals('def'))
             ),
        ]
        for source_lines, num_chars_to_consume_before, expected_instr_arg, expected_source in test_cases:
            with self.subTest():
                source = source3(source_lines)
                source.consume_part_of_current_line(num_chars_to_consume_before)
                instruction = self.parser.parse(source)
                self.assertIsInstance(instruction, Instruction,
                                      'Expects the Instruction to be returned')
                assert isinstance(instruction, Instruction)
                self.assertEqual(expected_instr_arg, instruction.argument,
                                 'Instruction argument')
                expected_source.apply_with_message(self, source, 'source')
