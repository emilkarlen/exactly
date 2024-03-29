import unittest

from exactly_lib.impls.types.string_ import parse_rich_string as sut
from exactly_lib.section_document import syntax
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source, remaining_source_lines
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.string_.test_resources import here_doc_assertion_utils as hd
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenarios))
    return ret_val


class TestFailingScenarios(unittest.TestCase):
    def test_fail_when_document_is_mandatory_but_is_not_given(self):
        parser = sut.HereDocParser(True)
        test_cases = [
            '',
            '    ',
        ]
        for first_line in test_cases:
            with self.subTest(msg='remaining source: ' + repr(first_line)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(remaining_source(first_line))

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
                parser = sut.HereDocParser(is_mandatory)
                with self.subTest(msg='mandatory: ' + repr(is_mandatory)):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(remaining_source(first_line))

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
                'NOT_MARKER',
            ],
        ]
        for following_lines in following_lines_cases:
            for is_mandatory in [False, True]:
                parser = sut.HereDocParser(is_mandatory)
                with self.subTest(msg=repr((is_mandatory, following_lines))):
                    with self.assertRaises(sut.HereDocumentContentsParsingException):
                        parser.parse(remaining_source(first_line, following_lines))


class SuccessfulCase:
    def __init__(self,
                 source_lines: list,
                 expected_document_contents: Assertion,
                 source_after_parse: Assertion):
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
                asrt_source.is_at_end_of_line(2)
            ),
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    'eof',
                ],
                expected_document_contents=
                hd.matches_resolved_value([]),
                source_after_parse=
                asrt_source.is_at_end_of_line(2)
            ),
            SuccessfulCase(
                source_lines=[
                    '<<-',
                    '-',
                ],
                expected_document_contents=
                hd.matches_resolved_value([])
                ,
                source_after_parse=
                asrt_source.is_at_end_of_line(2)
            ),
            SuccessfulCase(
                source_lines=[
                    '<<MARKER',
                    'MARKER',
                    ' after',
                ],
                expected_document_contents=
                hd.matches_resolved_value([])
                ,
                source_after_parse=
                asrt_source.is_at_end_of_line(2)
            ),
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    'single line contents',
                    'eof',
                ],
                expected_document_contents=
                hd.matches_resolved_value(['single line contents']),
                source_after_parse=
                asrt_source.is_at_end_of_line(3)
            ),
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
                asrt_source.is_at_end_of_line(4)
            ),
        ]
        for case in cases:
            self._check_case(case)

    def test_here_document_with_symbol_references(self):
        symbol1 = StringConstantSymbolContext('symbol_1_name', 'symbol 1 value')
        symbol2 = StringConstantSymbolContext('symbol_2_name', 'symbol 2 value')
        symbol3 = StringConstantSymbolContext('symbol_3_name', 'symbol 3 value')
        line_with_sym_ref_template = 'before symbol {symbol} after symbol'
        line_with_two_sym_refs_template = '{first_symbol} between symbols {second_symbol}'
        cases = [
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    line_with_sym_ref_template.format(
                        symbol=symbol1.name__sym_ref_syntax),
                    'eof',
                    'following line',
                ],
                expected_document_contents=
                hd.matches_resolved_value([
                    line_with_sym_ref_template.format(
                        symbol=symbol1.str_value),
                ],
                    symbol_references=[
                        symbol1.reference__w_str_rendering,
                    ],
                    symbols=symbol1.symbol_table
                ),
                source_after_parse=asrt_source.is_at_end_of_line(3),
            ),
            SuccessfulCase(
                source_lines=[
                    '<<eof',
                    line_with_sym_ref_template.format(
                        symbol=symbol1.name__sym_ref_syntax),
                    line_with_two_sym_refs_template.format(
                        first_symbol=symbol2.name__sym_ref_syntax,
                        second_symbol=symbol3.name__sym_ref_syntax),
                    'eof',
                    'following line',
                ],
                expected_document_contents=
                hd.matches_resolved_value([
                    line_with_sym_ref_template.format(
                        symbol=symbol1.str_value),
                    line_with_two_sym_refs_template.format(
                        first_symbol=symbol2.str_value,
                        second_symbol=symbol3.str_value),
                ],
                    symbol_references=[
                        symbol1.reference__w_str_rendering,
                        symbol2.reference__w_str_rendering,
                        symbol3.reference__w_str_rendering,
                    ],
                    symbols=SymbolContext.symbol_table_of_contexts([
                        symbol1,
                        symbol2,
                        symbol3
                    ],
                    )
                ),
                source_after_parse=asrt_source.is_at_end_of_line(4),
            ),
        ]
        for case in cases:
            self._check_case(case)

    def _check_case(self, case: SuccessfulCase):
        for is_mandatory in [False, True]:
            parser = sut.HereDocParser(is_mandatory)
            with self.subTest(source_lines=case.source_lines,
                              is_mandatory=str(is_mandatory)):
                source = remaining_source_lines(case.source_lines)
                actual = parser.parse(source)
                case.expected_document_contents.apply_with_message(self, actual,
                                                                   'sdv')
                case.source_after_parse.apply_with_message(self, source,
                                                           'source')

    def test_document_is_not_mandatory_and_not_present(self):
        some_white_space = '    '
        source_cases = [
            ([
                 '',
             ],
             asrt_source.is_at_end_of_line(1)),
            ([
                 some_white_space,
             ],
             asrt_source.assert_source(
                 current_line_number=asrt.equals(1),
                 remaining_part_of_current_line=asrt.equals(some_white_space)
             )),
            ([
                 '',
                 'line after',
             ],
             asrt_source.is_at_end_of_line(1)),
        ]
        parser = sut.HereDocParser(False)
        for source_lines, source_assertion in source_cases:
            with self.subTest(msg=repr((source_lines, source_assertion))):
                source = remaining_source_lines(source_lines)
                actual = parser.parse(source)
                self.assertIsNone(actual, 'return value from parsing')
                source_assertion.apply_with_message(self, source, 'source')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
