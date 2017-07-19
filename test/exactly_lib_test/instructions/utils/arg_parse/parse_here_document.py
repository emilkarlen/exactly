import unittest

from exactly_lib.instructions.utils.arg_parse import parse_here_document as sut
from exactly_lib.instructions.utils.arg_parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.section_document import syntax
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.parser_implementations.optional_description_and_instruction_parser import \
    source_is_at_end
from exactly_lib_test.section_document.test_resources.parse_source import source_is_not_at_end, is_at_beginning_of_line
from exactly_lib_test.symbol.test_resources import here_doc_assertion_utils as hd
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_with_string_values_from_name_and_value
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.parse import remaining_source, remaining_source_lines
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenarios))
    return ret_val


class TestFailingScenarios(unittest.TestCase):
    def test_fail_when_document_is_mandatory_but_is_not_given(self):
        test_cases = [
            '',
            '    ',
        ]
        for first_line in test_cases:
            with self.subTest(msg='remaining source: ' + repr(first_line)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_as_last_argument(True, remaining_source(first_line))

    def test_fail_when_invalid_here_document_argument(self):
        first_line_cases = [
            '<<MARKER superfluous_argument',
            '<<MARKER superfluous argument',
            '\'<<MARKER\'',
        ]
        test_cases = [
            False,
            True,
        ]
        for first_line in first_line_cases:
            for is_mandatory in test_cases:
                with self.subTest(msg='mandatory: ' + repr(is_mandatory)):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_as_last_argument(is_mandatory, remaining_source(first_line))

    def test_fail_when_end_marker_not_found(self):
        first_line = '<<MARKER'
        following_lines_cases = [
            [
                'not marker',
                syntax.section_header('section-name'),
            ],
            [
                'not marker',
            ],
            [],
            [
                '   MARKER',
            ],
            [
                'MARKER    ',
            ],
            [
                'NOTMARKER',
            ],
        ]
        for following_lines in following_lines_cases:
            for is_mandatory in [False, True]:
                with self.subTest(msg=repr((is_mandatory, following_lines))):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_as_last_argument(is_mandatory,
                                                   remaining_source(first_line, following_lines))


class SuccessfulCase:
    def __init__(self,
                 source_lines: list,
                 expected_document_contents: asrt.ValueAssertion,
                 source_after_parse: asrt.ValueAssertion):
        self.source_lines = source_lines
        self.expected_document_contents = expected_document_contents
        self.source_after_parse = source_after_parse


class TestSuccessfulScenarios(unittest.TestCase):
    def test_constant_here_document_is_given(self):
        cases = [
            SuccessfulCase(
                source_lines=[
                    '<<MARKER',
                    'MARKER',
                ],
                expected_document_contents=
                hd.matches_resolved_value([]),
                source_after_parse=
                source_is_at_end),
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    'eof',
                ],
                expected_document_contents=
                hd.matches_resolved_value([]),
                source_after_parse=
                source_is_at_end),
            SuccessfulCase(
                source_lines=[
                    '<<MARKER',
                    'MARKER',
                    ' after',
                ],
                expected_document_contents=
                hd.matches_resolved_value([]),
                source_after_parse=
                source_is_not_at_end(current_line_number=asrt.equals(3),
                                     remaining_part_of_current_line=asrt.equals(' after'))),
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    'single line contents',
                    'eof',
                ],
                expected_document_contents=
                hd.matches_resolved_value(['single line contents']),
                source_after_parse=
                source_is_at_end),
            SuccessfulCase(
                source_lines=[
                    '<<EOF',
                    'first line',
                    'second line',
                    'EOF',
                    'line after',
                ],
                expected_document_contents=
                hd.matches_resolved_value(['first line',
                                           'second line',
                                           ]),
                source_after_parse=
                source_is_not_at_end(current_line_number=asrt.equals(5),
                                     remaining_part_of_current_line=asrt.equals('line after'))),
        ]
        for case in cases:
            self._check_case(case)

    def test_here_document_with_symbol_references(self):
        symbol1 = NameAndValue('symbol_1_name', 'symbol 1 value')
        symbol2 = NameAndValue('symbol_2_name', 'symbol 2 value')
        symbol3 = NameAndValue('symbol_3_name', 'symbol 3 value')
        line_with_sym_ref_template = 'before symbol {symbol} after symbol'
        line_with_two_sym_refs_template = '{first_symbol} between symbols {second_symbol}'
        cases = [
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    line_with_sym_ref_template.format(
                        symbol=symbol_reference_syntax_for_name(symbol1.name)),
                    'eof',
                    'following line',
                ],
                expected_document_contents=
                hd.matches_resolved_value([
                    line_with_sym_ref_template.format(
                        symbol=symbol1.value),
                ],
                    symbol_references=[
                        hd.reference_to(symbol1),
                    ],
                    symbols=symbol_table_with_string_values_from_name_and_value([
                        symbol1,
                    ],
                    )
                ),
                source_after_parse=is_at_beginning_of_line(4),
            ),
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    line_with_sym_ref_template.format(
                        symbol=symbol_reference_syntax_for_name(symbol1.name)),
                    line_with_two_sym_refs_template.format(
                        first_symbol=symbol_reference_syntax_for_name(symbol2.name),
                        second_symbol=symbol_reference_syntax_for_name(symbol3.name)),
                    'eof',
                    'following line',
                ],
                expected_document_contents=
                hd.matches_resolved_value([
                    line_with_sym_ref_template.format(
                        symbol=symbol1.value),
                    line_with_two_sym_refs_template.format(
                        first_symbol=symbol2.value,
                        second_symbol=symbol3.value),
                ],
                    symbol_references=[
                        hd.reference_to(symbol1),
                        hd.reference_to(symbol2),
                        hd.reference_to(symbol3),
                    ],
                    symbols=symbol_table_with_string_values_from_name_and_value([
                        symbol1,
                        symbol2,
                        symbol3
                    ],
                    )
                ),
                source_after_parse=is_at_beginning_of_line(5),
            ),
        ]
        for case in cases:
            self._check_case(case)

    def _check_case(self, case: SuccessfulCase):
        for is_mandatory in [False, True]:
            with self.subTest(source_lines=case.source_lines,
                              is_mandatory=str(is_mandatory)):
                source = remaining_source_lines(case.source_lines)
                actual = sut.parse_as_last_argument(is_mandatory, source)
                case.expected_document_contents.apply_with_message(self, actual,
                                                                   'resolver')
                case.source_after_parse.apply_with_message(self, source,
                                                           'source')

    def test_document_is_not_mandatory_and_not_present(self):
        source_cases = [
            ([
                 '',
             ],
             source_is_at_end),
            ([
                 '    ',
             ],
             source_is_at_end),
            ([
                 '',
                 'line after',
             ],
             source_is_not_at_end(current_line_number=asrt.equals(2),
                                  remaining_part_of_current_line=asrt.equals('line after'))),
        ]
        for source_lines, source_assertion in source_cases:
            with self.subTest(msg=repr((source_lines, source_assertion))):
                source = remaining_source_lines(source_lines)
                actual = sut.parse_as_last_argument(False, source)
                self.assertIsNone(actual, 'return value from parsing')
                source_assertion.apply_with_message(self, source, 'source')


if __name__ == '__main__':
    unittest.main()
