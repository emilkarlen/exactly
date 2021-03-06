import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers import section_element_parsers as sut
from exactly_lib.section_document.model import ElementType
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedNonInstructionElement
from exactly_lib.section_document.section_element_parsing import SectionElementError, \
    UnrecognizedSectionElementSourceError, RecognizedSectionElementSourceError
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.document_assertions import equals_empty_element, \
    equals_comment_element, matches_instruction
from exactly_lib_test.section_document.test_resources.element_assertions import matches_instruction_info
from exactly_lib_test.section_document.test_resources.element_parsers import SectionElementParserThatReturnsNone, \
    SectionElementParserThatReturnsConstantAndConsumesCurrentLine, \
    SectionElementParserThatRaisesRecognizedSectionElementSourceError, \
    SectionElementParserThatRaisesUnrecognizedSectionElementSourceError
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParserFromSequenceOfParsers),
        unittest.makeSuite(TestStandardSyntaxElementParser),
    ])


class TestParserFromSequenceOfParsers(unittest.TestCase):
    def test_all_fail_None_SHOULD_be_returned_WHEN_all_parsers_return_None(self):
        # ARRANGE #
        source_text = 'first line'
        cases = [
            NameAndValue('no parsers',
                         [])
            ,
            NameAndValue('one parser',
                         [SectionElementParserThatReturnsNone()]
                         ),
            NameAndValue('more than one parser',
                         [SectionElementParserThatReturnsNone(),
                          SectionElementParserThatReturnsNone()]
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = ParseSource(source_text)
                parser = sut.ParserFromSequenceOfParsers(case.value)
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                # ASSERT #
                self.assertIsNone(actual, 'return value from parser')
                expected_source = asrt_source.source_is_not_at_end(remaining_source=asrt.equals(source_text))
                expected_source.apply_with_message(self, source, 'source')

    def test_all_fail_unrecognized_element_SHOULD_be_raised_WHEN_all_parsers_fail_and_last_parser_raises_UE(self):
        # ARRANGE #
        source_text = 'first line'
        err_msg = 'error message in exception'
        cases = [
            NameAndValue('one parser',
                         [SectionElementParserThatRaisesUnrecognizedSectionElementSourceError(err_msg)]
                         ),
            NameAndValue('more than one parser - first parser returns None',
                         [SectionElementParserThatReturnsNone(),
                          SectionElementParserThatRaisesUnrecognizedSectionElementSourceError(err_msg)]
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = ParseSource(source_text)
                parser = sut.ParserFromSequenceOfParsers(case.value)
                # ACT #
                with self.assertRaises(UnrecognizedSectionElementSourceError) as cm:
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                self.assertEqual(err_msg, cm.exception.message,
                                 'error message in exception')

    def test_all_fail_recognized_element_SHOULD_be_raised_WHEN_a_parser_raises_RE(self):
        # ARRANGE #
        returned_element = ParsedNonInstructionElement(single_line_sequence(1, 'parsed by successful parser'),
                                                       ElementType.EMPTY)
        source_text = 'first line'
        err_msg = 'error message in RE exception'
        cases = [
            NameAndValue('single parser raises RE',
                         [SectionElementParserThatRaisesRecognizedSectionElementSourceError(err_msg)]
                         ),
            NameAndValue('1:st parser fails by returning None, 2nd=last parsers - last parser raises RE',
                         [SectionElementParserThatReturnsNone(),
                          SectionElementParserThatRaisesRecognizedSectionElementSourceError(err_msg)]
                         ),
            NameAndValue('1:st parser fails by raising UnrecognizedError, 2nd=last parsers - last parser raises RE',
                         [SectionElementParserThatRaisesUnrecognizedSectionElementSourceError('err msg of UE'),
                          SectionElementParserThatRaisesRecognizedSectionElementSourceError(err_msg)]
                         ),
            NameAndValue('first parser raises RE, following parser succeeds',
                         [SectionElementParserThatRaisesRecognizedSectionElementSourceError(err_msg),
                          SectionElementParserThatReturnsConstantAndConsumesCurrentLine(returned_element),
                          ]
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = ParseSource(source_text)
                parser = sut.ParserFromSequenceOfParsers(case.value)
                # ACT #
                with self.assertRaises(RecognizedSectionElementSourceError) as cm:
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                self.assertEqual(err_msg, cm.exception.message,
                                 'error message in exception')

    def test_element_from_first_parser_that_returns_an_element_SHOULD_be_returned(self):
        # ARRANGE #
        source_lines = ['first line',
                        'second line']
        expected_returned_element = ParsedNonInstructionElement(single_line_sequence(1, 'expected'),
                                                                ElementType.EMPTY)
        unexpected_returned_element = ParsedNonInstructionElement(single_line_sequence(1, 'unexpected'),
                                                                  ElementType.EMPTY)
        cases = [
            NameAndValue('single successful parser',
                         [
                             SectionElementParserThatReturnsConstantAndConsumesCurrentLine(expected_returned_element),
                         ])
            ,
            NameAndValue('more than one successful parser',
                         [
                             SectionElementParserThatReturnsConstantAndConsumesCurrentLine(expected_returned_element),
                             SectionElementParserThatReturnsConstantAndConsumesCurrentLine(unexpected_returned_element),
                         ]
                         ),
            NameAndValue('first parser is unsuccessful - returns None',
                         [
                             SectionElementParserThatReturnsNone(),
                             SectionElementParserThatReturnsConstantAndConsumesCurrentLine(expected_returned_element),
                         ]
                         ),
            NameAndValue('first parser is unsuccessful - throws unrecognized element',
                         [
                             SectionElementParserThatRaisesUnrecognizedSectionElementSourceError(),
                             SectionElementParserThatReturnsConstantAndConsumesCurrentLine(expected_returned_element),
                         ]
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = source_of_lines(source_lines)
                parser = sut.ParserFromSequenceOfParsers(case.value)
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                # ASSERT #
                self.assertIs(expected_returned_element,
                              actual, 'return value from parser')
                expected_source = asrt_source.is_at_beginning_of_line(2)
                expected_source.apply_with_message(self, source, 'source')

    def test_exception_SHOULD_be_raised_WHEN_a_parser_to_try_raises_an_exception(self):
        # ARRANGE #
        source_lines = ['first line',
                        'second line']
        returned_element = ParsedNonInstructionElement(single_line_sequence(1, 'expected'),
                                                       ElementType.EMPTY)
        cases = [
            NameAndValue('single failing parser',
                         [
                             SectionElementParserThatRaisesRecognizedSectionElementSourceError(),
                         ])
            ,
            NameAndValue('failing parser followed by successful parser',
                         [
                             SectionElementParserThatReturnsNone(),
                             SectionElementParserThatRaisesRecognizedSectionElementSourceError(),
                             SectionElementParserThatReturnsConstantAndConsumesCurrentLine(returned_element),
                         ]
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = source_of_lines(source_lines)
                parser = sut.ParserFromSequenceOfParsers(case.value)
                # ACT & ASSERT #
                with self.assertRaises(SectionElementError):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestStandardSyntaxElementParser(unittest.TestCase):
    def test_parse_empty_line(self):
        parser = sut.standard_syntax_element_parser(_InstructionParserForInstructionLineThatStartsWith('I'))
        test_cases = [([' '], 1, ''),
                      (['  \t  '], 1, ''),
                      (['  ', '', 'remaining'], 2, 'remaining'),
                      (['  ', '', ''], 3, ''),
                      (['  ', 'remaining'], 1, 'remaining'),
                      ]
        for source_lines, num_empty_lines, remaining_source in test_cases:
            with self.subTest(source_lines=source_lines,
                              remaining_source=remaining_source):
                # ARRANGE #
                source = _source_for_lines(source_lines)
                # ACT #
                element = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                # ASSERT #
                element_assertion = equals_empty_element(LineSequence(1, source_lines[:num_empty_lines]))
                element_assertion.apply_with_message(self, element, 'element')
                self.assertEqual(remaining_source,
                                 source.remaining_source,
                                 'Remaining source')

    def test_parse_comment_line(self):
        parser = sut.standard_syntax_element_parser(_InstructionParserForInstructionLineThatStartsWith('I'))
        test_cases = [(['# comment'], 1, ''),
                      (['  #  comment'], 1, ''),
                      (['# A', '  # B'], 2, ''),
                      (['# A', '  # B', ' '], 2, ' '),
                      (['#   ', 'remaining'], 1, 'remaining'),
                      ]
        for source_lines, num_comment_lines, remaining_source in test_cases:
            with self.subTest(source_lines=source_lines,
                              remaining_source=remaining_source):
                # ARRANGE #
                source = _source_for_lines(source_lines)
                # ACT #
                element = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                # ASSERT #
                element_assertion = equals_comment_element(LineSequence(1, source_lines[:num_comment_lines]))
                element_assertion.apply_with_message(self, element, 'element')
                self.assertEqual(remaining_source,
                                 source.remaining_source,
                                 'Remaining source')

    def test_parse_single_line_instruction(self):
        parser = sut.standard_syntax_element_parser(_InstructionParserForInstructionLineThatStartsWith('I'))
        test_cases = [(['I arguments'], ''),
                      (['I arguments', 'remaining'], 'remaining'),
                      (['I line 1', 'I line 2', 'not an instruction'], 'not an instruction'),
                      ]
        for source_lines, remaining_source in test_cases:
            with self.subTest(source_lines=source_lines,
                              remaining_source=remaining_source):
                source = _source_for_lines(source_lines)
                # ACT #
                element = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
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
        parser = sut.standard_syntax_element_parser(_InstructionParserThatGivesConstant(expected))
        source = _source_for_lines(['ignored', 'source', 'lines'])
        # ACT #
        element = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
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
              fs_location_info: FileSystemLocationInfo,
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
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> sut.ParsedInstruction:
        return self.return_value


class Instruction(model.Instruction):
    pass


def _source_for_lines(source_lines: list) -> ParseSource:
    source_string = '\n'.join(source_lines)
    return ParseSource(source_string)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
