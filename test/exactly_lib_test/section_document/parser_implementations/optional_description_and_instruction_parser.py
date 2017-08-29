import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser, \
    InstructionAndDescription
from exactly_lib_test.section_document.test_resources.parse_source import source3
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source, source_is_at_end
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseWithDescription)
    ])


class SingleInstructionParserThatConsumesCurrentLine(InstructionParser):
    def parse(self, source: ParseSource) -> model.Instruction:
        ret_val = Instruction(source.current_line_number,
                              source.remaining_part_of_current_line)
        source.consume_current_line()
        return ret_val


class TestParseWithDescription(unittest.TestCase):
    sut = InstructionWithOptionalDescriptionParser(SingleInstructionParserThatConsumesCurrentLine())

    def test_no_description(self):
        source_lines = ['instruction']
        source = source3(source_lines)
        expectation = Expectation(description=asrt.is_none,
                                  source=source_is_at_end,
                                  instruction=assert_instruction(1, 'instruction'))
        arrangement = Arrangement(self.sut, source)
        check(self, expectation, arrangement)

    def test_fail_when_there_is_a_description_but_no_following_instruction(self):
        test_cases = [
            ['\'description\'',
             ],
            ['\'description\'        ',
             ],
            ['\'description\'',
             '',
             ],
            ['\'multi line description',
             '\'',
             ],
            ['\'multi line description',
             '\'',
             '',
             ],
        ]
        for source_lines in test_cases:
            with self.subTest(source_lines=source_lines):
                source = source3(source_lines)
                with self.assertRaises(SourceError):
                    self.sut.parse(source)

    def test_description_and_instruction_on_single_line(self):
        source_and_description_variants = [
            (["'single line, single quotes' instruction"],
             'single line, single quotes', 'instruction'),
            (['       "single line, indented, double quotes"    other-instruction'],
             'single line, indented, double quotes', 'other-instruction'),
        ]
        for source_lines, expected_description, expected_instruction in source_and_description_variants:
            with self.subTest(source_lines=source_lines,
                              expected_description=expected_description,
                              expected_instruction=expected_instruction):
                source = source3(source_lines)
                expectation = Expectation(description=asrt.equals(expected_description),
                                          source=source_is_at_end,
                                          instruction=assert_instruction(1, expected_instruction))
                arrangement = Arrangement(self.sut, source)
                check(self, expectation, arrangement)

    def test_description_on_single_line_and_instruction_on_line_after(self):
        source_and_description_variants = [
            (["'single line, single quotes'",
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, single quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(2, 'instruction')),
             ),
            (["'single line, single quotes'",
              '',
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, single quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(3, 'instruction')),
             ),
            (["   'single line, indented, single quotes'",
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, indented, single quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(2, 'instruction')),
             ),
            (['       "single line, indented, double quotes"    ',
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, indented, double quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(2, 'instruction')),
             ),
            (['       "single line, indented, double quotes"    ',
              '     ',
              '',
              'instruction',
              ],
             Expectation(description=asrt.Equals('single line, indented, double quotes'),
                         source=source_is_at_end,
                         instruction=assert_instruction(4, 'instruction')),
             ),
        ]
        for description_lines, expectation in source_and_description_variants:
            with self.subTest(description_lines=description_lines):
                source = source3(description_lines)
                arrangement = Arrangement(self.sut, source)
                check(self, expectation, arrangement)

    def test_ignore_comment_lines_between_description_and_instruction(self):
        source_and_description_variants = [
            (['\'description\'',
              syntax.LINE_COMMENT_MARKER,
              'instruction',
              ],
             Expectation(description=asrt.Equals('description'),
                         source=source_is_at_end,
                         instruction=assert_instruction(3, 'instruction')),
             ),
            (['\'description\'',
              '     ' + syntax.LINE_COMMENT_MARKER + ' comment text   ',
              'instruction',
              ],
             Expectation(description=asrt.Equals('description'),
                         source=source_is_at_end,
                         instruction=assert_instruction(3, 'instruction')),
             ),
            (['\'description\'',
              '',
              syntax.LINE_COMMENT_MARKER,
              '',
              'Instruction',
              ],
             Expectation(description=asrt.Equals('description'),
                         source=source_is_at_end,
                         instruction=assert_instruction(5, 'Instruction')),
             ),
            (['\'description line 1',
              'description line 2\'',
              syntax.LINE_COMMENT_MARKER,
              'Instruction',
              ],
             Expectation(description=asrt.Equals('description line 1\ndescription line 2'),
                         source=source_is_at_end,
                         instruction=assert_instruction(4, 'Instruction')),
             ),
            (['\'description line 1',
              'description line 2\'',
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
                source = source3(description_lines)
                arrangement = Arrangement(self.sut, source)
                check(self, expectation, arrangement)

    def test_multi_line_description(self):
        test_cases = [
            (['\'first line of description',
              'second line of description\'',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(3, 'instruction line'),
                         source_is_at_end),
             ),
            (['\'first line of description',
              'second line of description\'',
              '',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(4, 'instruction line'),
                         source_is_at_end),
             ),
            (['\'first line of description',
              'second line of description\'      ',
              '    ',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(4, 'instruction line'),
                         source_is_at_end),
             ),
            (['\'first line of description',
              'second line of description\'   instruction source'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(2, 'instruction source'),
                         source_is_at_end),
             ),
        ]
        for source_lines, expectation in test_cases:
            with self.subTest(source_lines=str(source_lines)):
                check(self, expectation,
                      Arrangement(self.sut, source3(source_lines)))

    def test_strip_space_from_description(self):
        test_cases = [
            (['\'   first line of description',
              'second line of description  \'',
              'instruction line'],
             Expectation(asrt.equals('first line of description\nsecond line of description'),
                         assert_instruction(3, 'instruction line'),
                         assert_source(is_at_eof=asrt.equals(True),
                                       has_current_line=asrt.equals(False))),
             ),
            (['\'',
              'first line of description',
              '  second line of description',
              '',
              '\'',
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
                      Arrangement(self.sut, source3(source_lines)))


class Expectation(tuple):
    def __new__(cls,
                description: asrt.ValueAssertion = asrt.anything_goes(),
                instruction: asrt.ValueAssertion = asrt.anything_goes(),
                source: asrt.ValueAssertion = asrt.anything_goes()):
        return tuple.__new__(cls, (description, instruction, source))

    @property
    def description(self) -> asrt.ValueAssertion:
        return self[0]

    @property
    def instruction(self) -> asrt.ValueAssertion:
        return self[1]

    @property
    def source(self) -> asrt.ValueAssertion:
        return self[2]

    def apply(self, put: unittest.TestCase,
              instruction_and_description: InstructionAndDescription,
              source: ParseSource):
        put.assertIsInstance(instruction_and_description, InstructionAndDescription,
                             'instruction_and_description')
        put.assertIsInstance(instruction_and_description.instruction, Instruction,
                             'instruction')
        self.description.apply_with_message(put, instruction_and_description.description,
                                            'description')
        self.instruction.apply_with_message(put, instruction_and_description.instruction,
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
    result = arrangement.parser.parse(arrangement.source)
    expectation.apply(put, result, arrangement.source)


def assert_instruction(first_line_number: int,
                       source_string: str) -> asrt.ValueAssertion:
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
