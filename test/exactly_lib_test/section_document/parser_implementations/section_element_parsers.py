import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.model import ElementType
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import section_element_parsers as sut
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line
from exactly_lib_test.section_document.test_resources.assertions import assert_equals_line


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestStandardSyntaxElementParser))
    return ret_val


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
                element = parser.parse(source)
                # ASSERT #
                self.assertEqual(ElementType.EMPTY,
                                 element.element_type,
                                 'Element type')
                assert_equals_line(self,
                                   Line(1, source_lines[0]),
                                   element.first_line)
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
                element = parser.parse(source)
                # ASSERT #
                self.assertEqual(ElementType.COMMENT,
                                 element.element_type,
                                 'Element type')
                assert_equals_line(self,
                                   Line(1, source_lines[0]),
                                   element.first_line)
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
                element = parser.parse(source)
                self.assertEqual(ElementType.INSTRUCTION,
                                 element.element_type,
                                 'Element type')
                self.assertIsInstance(element.instruction,
                                      Instruction,
                                      'Instruction class')
                assert_equals_line(self,
                                   Line(1, source_lines[0]),
                                   element.first_line)
                self.assertEqual(remaining_source,
                                 source.remaining_source,
                                 'Remaining source')


class _InstructionParserForInstructionLineThatStartsWith(sut.InstructionAndDescriptionParser):
    def __init__(self, instruction_line_identifier: str):
        self.instruction_line_identifier = instruction_line_identifier

    def parse(self, source: ParseSource) -> sut.InstructionAndDescription:
        first_line_number = source.current_line_number
        dummy_source = line_source.LineSequence(first_line_number, (source.current_line_text,))
        is_instruction = False
        while not source.is_at_eof and source.current_line_text.startswith(self.instruction_line_identifier):
            source.consume_current_line()
            is_instruction = True
        if not is_instruction:
            raise ValueError('Not an instruction')
        return sut.InstructionAndDescription(Instruction(), dummy_source, None)


class Instruction(model.Instruction):
    pass


def _source_for_lines(source_lines: list) -> ParseSource:
    source_string = '\n'.join(source_lines)
    return ParseSource(source_string)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
