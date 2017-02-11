import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionParser, \
    InstructionAndDescription
from exactly_lib.section_document.parser_implementations.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib_test.test_resources.parse import source3
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseWithDescription)
    ])


class SingleInstructionParserThatSucceeds(InstructionParser):
    def parse(self, source: ParseSource) -> model.Instruction:
        ret_val = Instruction(source.current_line_number,
                              source.current_line_text)
        source.consume_current_line()
        return ret_val


class TestParseWithDescription(unittest.TestCase):
    sut = InstructionWithOptionalDescriptionParser(SingleInstructionParserThatSucceeds())

    def test_no_description(self):
        source_lines = ['instruction']
        source = source3(source_lines)
        expectation = Expectation(description=va.is_none,
                                  source=source_is_at_end,
                                  instruction=instruction_is(1, 'instruction'))
        arrangement = Arrangement(self.sut, source)
        check(self, expectation, arrangement)

    def test_description_on_single_line_and_instruction_on_line_after(self):
        source_and_description_variants = [
            (["'single line, single quotes'"],
             'single line, single quotes'),
            (["   'single line, indented, single quotes'"],
             'single line, indented, single quotes'),
            (['       "single line, indented, double quotes"'],
             'single line, indented, double quotes'),
        ]
        for description_lines, expected_description in source_and_description_variants:
            with self.subTest(description_lines=description_lines,
                              expected_description=expected_description):
                self._do_test(description_lines=description_lines,
                              expected_description=expected_description)

    def _do_test(self, description_lines: list, expected_description: str):
        instruction_source_lines = ['instruction']
        source = source3(description_lines + instruction_source_lines)
        expectation = Expectation(description=va.Equals(expected_description),
                                  source=source_is_at_end,
                                  instruction=instruction_is(2, 'instruction'))
        arrangement = Arrangement(self.sut, source)
        check(self, expectation, arrangement)


class Expectation(tuple):
    def __new__(cls,
                description: va.ValueAssertion = va.anything_goes(),
                instruction: va.ValueAssertion = va.anything_goes(),
                source: va.ValueAssertion = va.anything_goes()):
        return tuple.__new__(cls, (description, instruction, source))

    @property
    def description(self) -> va.ValueAssertion:
        return self[0]

    @property
    def instruction(self) -> va.ValueAssertion:
        return self[1]

    @property
    def source(self) -> va.ValueAssertion:
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


def instruction_is(first_line_number: int,
                   source_string: str) -> va.ValueAssertion:
    return va.And([
        va.sub_component('first_line_number', Instruction.first_line_number.fget,
                         va.Equals(first_line_number)),
        va.sub_component('source_string', Instruction.source_string.fget,
                         va.Equals(source_string))
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


source_is_at_end = va.And([
    va.sub_component('is_at_eof', ParseSource.is_at_eof.fget,
                     va.Boolean(True)),
    va.sub_component('remaining_source', ParseSource.remaining_source.fget,
                     va.Equals(''))
])
