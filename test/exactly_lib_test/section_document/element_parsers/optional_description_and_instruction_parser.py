import unittest
from typing import Sequence

from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.defs import DESCRIPTION_DELIMITER
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedInstruction
from exactly_lib.section_document.section_element_parsing import UnrecognizedSectionElementSourceError, \
    RecognizedSectionElementSourceError
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source, source_is_at_end
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseWithDescription)


class SingleInstructionParserThatConsumesCurrentLine(InstructionParserWithoutSourceFileLocationInfo):
    def parse_from_source(self, source: ParseSource) -> model.Instruction:
        ret_val = Instruction(source.current_line_number,
                              source.remaining_part_of_current_line)
        source.consume_current_line()
        return ret_val


class TestParseWithDescription(unittest.TestCase):
    sut = InstructionWithOptionalDescriptionParser(SingleInstructionParserThatConsumesCurrentLine())

    def test_no_description(self):
        source_lines = ['instruction']
        source = _source_of_lines(source_lines)
        expectation = Expectation(description=asrt.is_none,
                                  source=source_is_at_end,
                                  instruction=assert_instruction(1, 'instruction'))
        arrangement = Arrangement(self.sut, source)
        check(self, expectation, arrangement)

    def test_fail_when_there_is_a_description_but_no_following_instruction(self):
        test_cases = [
            ['{d}description{d}',
             ],
            ['{d}description{d}        ',
             ],
            ['{d}description{d}',
             '',
             ],
            ['{d}multi line description',
             '{d}',
             ],
            ['{d}multi line description',
             '{d}',
             '',
             ],
        ]
        for source_lines in test_cases:
            with self.subTest(source_lines=source_lines):
                source = _source_of_lines(source_lines)
                remaining_source_before = source.remaining_source
                with self.assertRaises(UnrecognizedSectionElementSourceError):
                    self.sut.parse(ARBITRARY_FS_LOCATION_INFO, source)
                self.assertEqual(remaining_source_before,
                                 source.remaining_source,
                                 'no source should have been consumed')

    def test_fail_WHEN_description_has_invalid_syntax(self):
        test_cases = [
            NameAndValue('No ending quote, single line',
                         ['{d}description',
                          ]),
            NameAndValue('No ending quote, would-be-instruction on following line',
                         ['{d}description',
                          'would_be_instruction']),
        ]
        for name, source_lines in test_cases:
            with self.subTest(name):
                source = _source_of_lines(source_lines)
                with self.assertRaises(RecognizedSectionElementSourceError):
                    self.sut.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_description_and_instruction_on_single_line(self):
        source_and_description_variants = [
            (['{d}single line, single quotes{d} instruction'],
             'single line, single quotes',
             'instruction'),
            (['       {d}single line, indented{d}    other-instruction'],
             'single line, indented',
             'other-instruction'),
        ]
        for source_lines, expected_description, expected_instruction in source_and_description_variants:
            with self.subTest(source_lines=source_lines,
                              expected_description=expected_description,
                              expected_instruction=expected_instruction):
                source = _source_of_lines(source_lines)
                expectation = Expectation(description=asrt.equals(expected_description),
                                          source=source_is_at_end,
                                          instruction=assert_instruction(1, expected_instruction))
                arrangement = Arrangement(self.sut, source)
                check(self, expectation, arrangement)

    def test_description_on_single_line_and_instruction_on_line_after(self):
        source_and_description_variants = [
            (['{d}single line, single quotes{d}',
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, single quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(2, 'instruction')),
             ),
            (['{d}single line, single quotes{d}',
              '',
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, single quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(3, 'instruction')),
             ),
            (['   {d}single line, indented{d}',
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, indented'),
                         source=source_is_at_end,
                         instruction=assert_instruction(2, 'instruction')),
             ),
        ]
        for description_lines, expectation in source_and_description_variants:
            with self.subTest(description_lines=description_lines):
                source = _source_of_lines(description_lines)
                arrangement = Arrangement(self.sut, source)
                check(self, expectation, arrangement)

    def test_ignore_comment_lines_between_description_and_instruction(self):
        source_and_description_variants = [
            (['{d}description{d}',
              syntax.LINE_COMMENT_MARKER,
              'instruction',
              ],
             Expectation(description=asrt.Equals('description'),
                         source=source_is_at_end,
                         instruction=assert_instruction(3, 'instruction')),
             ),
            (['{d}description{d}',
              '     ' + syntax.LINE_COMMENT_MARKER + ' comment text   ',
              'instruction',
              ],
             Expectation(description=asrt.Equals('description'),
                         source=source_is_at_end,
                         instruction=assert_instruction(3, 'instruction')),
             ),
            (['{d}description{d}',
              '',
              syntax.LINE_COMMENT_MARKER,
              '',
              'Instruction',
              ],
             Expectation(description=asrt.Equals('description'),
                         source=source_is_at_end,
                         instruction=assert_instruction(5, 'Instruction')),
             ),
            (['{d}description line 1',
              'description line 2{d}',
              syntax.LINE_COMMENT_MARKER,
              'Instruction',
              ],
             Expectation(description=asrt.Equals('description line 1\ndescription line 2'),
                         source=source_is_at_end,
                         instruction=assert_instruction(4, 'Instruction')),
             ),
            (['{d}description line 1',
              'description line 2{d}',
              '',
              '' + syntax.LINE_COMMENT_MARKER,
              '' + syntax.LINE_COMMENT_MARKER,
              'Instruction',
              ],
             Expectation(description=asrt.Equals('description line 1\ndescription line 2'),
                         source=source_is_at_end,
                         instruction=assert_instruction(6, 'Instruction')),
             ),
        ]
        for description_lines, expectation in source_and_description_variants:
            with self.subTest(description_lines=description_lines):
                source = _source_of_lines(description_lines)
                arrangement = Arrangement(self.sut, source)
                check(self, expectation, arrangement)

    def test_multi_line_description(self):
        test_cases = [
            (['{d}first line of description',
              'second line of description{d}',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(3, 'instruction line'),
                         source_is_at_end),
             ),
            (['{d}first line of description',
              'second line of description{d}',
              '',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(4, 'instruction line'),
                         source_is_at_end),
             ),
            (['{d}first line of description',
              'second line of description{d}      ',
              '    ',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(4, 'instruction line'),
                         source_is_at_end),
             ),
            (['{d}first line of description',
              'second line of description{d}   instruction source'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(2, 'instruction source'),
                         source_is_at_end),
             ),
        ]
        for source_lines, expectation in test_cases:
            with self.subTest(source_lines=str(source_lines)):
                check(self, expectation,
                      Arrangement(self.sut, _source_of_lines(source_lines)))

    def test_strip_space_from_description(self):
        test_cases = [
            (['{d}   first line of description',
              'second line of description  {d}',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(3, 'instruction line'),
                         assert_source(is_at_eof=asrt.equals(True),
                                       has_current_line=asrt.equals(False))),
             ),
            (['{d}',
              'first line of description',
              '  second line of description',
              '',
              '{d}',
              'instruction source'],
             Expectation(asrt.equals('first line of description\n  second line of description'),
                         assert_instruction(6, 'instruction source'),
                         assert_source(is_at_eof=asrt.equals(True),
                                       has_current_line=asrt.equals(False))),
             ),
        ]
        for source_lines, expectation in test_cases:
            with self.subTest(source_lines=str(source_lines)):
                check(self, expectation,
                      Arrangement(self.sut, _source_of_lines(source_lines)))


class Expectation(tuple):
    def __new__(cls,
                description: Assertion[str] = asrt.anything_goes(),
                instruction: Assertion[model.Instruction] = asrt.anything_goes(),
                source: Assertion[ParseSource] = asrt.anything_goes()):
        return tuple.__new__(cls, (description, instruction, source))

    @property
    def description(self) -> Assertion:
        return self[0]

    @property
    def instruction(self) -> Assertion:
        return self[1]

    @property
    def source(self) -> Assertion:
        return self[2]

    def apply(self, put: unittest.TestCase,
              actual_parsed_instruction,
              source: ParseSource):
        put.assertIsInstance(actual_parsed_instruction, ParsedInstruction,
                             'ParsedInstruction')
        assert isinstance(actual_parsed_instruction, ParsedInstruction)  # Type info for IDE
        instruction_info = actual_parsed_instruction.instruction_info
        put.assertIsInstance(actual_parsed_instruction.instruction_info, model.InstructionInfo,
                             'instruction_info')
        assert isinstance(instruction_info, model.InstructionInfo)
        put.assertIsInstance(instruction_info.instruction, Instruction,
                             'instruction')
        self.description.apply_with_message(put, instruction_info.description,
                                            'description')
        self.instruction.apply_with_message(put, instruction_info.instruction,
                                            'instruction')
        self.source.apply_with_message(put, source,
                                       'source')


class Arrangement(tuple):
    def __new__(cls,
                parser: InstructionWithOptionalDescriptionParser,
                source: ParseSource,
                ):
        return tuple.__new__(cls, (parser, source))

    @property
    def parser(self) -> InstructionWithOptionalDescriptionParser:
        return self[0]

    @property
    def source(self) -> ParseSource:
        return self[1]


def check(put: unittest.TestCase,
          expectation: Expectation,
          arrangement: Arrangement):
    result = arrangement.parser.parse(ARBITRARY_FS_LOCATION_INFO,
                                      arrangement.source)
    expectation.apply(put, result, arrangement.source)


def assert_instruction(first_line_number: int,
                       source_string: str) -> Assertion:
    return asrt.And([
        asrt.sub_component('first_line_number', Instruction.first_line_number.fget,
                           asrt.Equals(first_line_number)),
        asrt.sub_component('source_string', Instruction.source_string.fget,
                           asrt.Equals(source_string))
    ])


class Instruction(model.Instruction):
    def __init__(self, first_line_number: int, source_string: str):
        self._first_line_number = first_line_number
        self._source_string = source_string

    @property
    def first_line_number(self) -> int:
        return self._first_line_number

    @property
    def source_string(self) -> str:
        return self._source_string


def _source_of_lines(lines: Sequence[str]) -> ParseSource:
    return source_of_lines([
        line.format(d=DESCRIPTION_DELIMITER)
        for line in lines

    ])
