import unittest
from typing import List

from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.ps_or_tp import parser_opt_parens as sut
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import PARSE_RESULT
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc, NSourceCase
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailureOfPlainParse),
        unittest.makeSuite(TestInvalidSyntaxForMissingEndParenthesis),
        unittest.makeSuite(TestSuccessfulParsing),
    ])


class TestSuccessfulParsing(unittest.TestCase):
    def test_wo_parentheses__from_parse_source(self):
        # ARRANGE #
        expected_int = 3

        for source_case in self.cases_wo_parentheses(expected_int):
            with self.subTest(source_case.name):
                # ACT & ASSERT #
                _check_parse_from_parse_source(
                    self,
                    source_case.source,
                    expected_parsed_value=expected_int,
                    expected_source_after_parse=source_case.expectation,
                )

    def test_w_parentheses__from_parse_source(self):
        # ARRANGE #
        expected_int = 72

        for case in self.cases_w_parentheses(expected_int):
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check_parse_from_parse_source(
                    self,
                    case.source,
                    expected_parsed_value=expected_int,
                    expected_source_after_parse=case.expectation,
                )

    def test_wo_parentheses__from_token_parser(self):
        # ARRANGE #
        expected_int = 3

        for source_case in self.cases_wo_parentheses(expected_int):
            with self.subTest(source_case.name):
                # ACT & ASSERT #
                _check_parse_from_token_parser(
                    self,
                    source_case.source,
                    expected_parsed_value=expected_int,
                    expected_source_after_parse=source_case.expectation,
                )

    def test_w_parentheses__from_token_parser(self):
        # ARRANGE #
        expected_int = 72

        for case in self.cases_w_parentheses(expected_int):
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check_parse_from_token_parser(
                    self,
                    case.source,
                    expected_parsed_value=expected_int,
                    expected_source_after_parse=case.expectation,
                )

    @staticmethod
    def cases_wo_parentheses(expected_int: int) -> List[NSourceCase]:
        return [
            NSourceCase(
                'plain int',
                ParseSource(str(expected_int)),
                asrt_source.is_at_end_of_line(1),
            ),
            NSourceCase(
                'plain int followed by other plain int',
                ParseSource(str(expected_int) + ' 77'),
                asrt_source.is_at_line(1, '77'),
            ),
            NSourceCase(
                'plain int followed by end parenthesis',
                ParseSource(str(expected_int) + ' )'),
                asrt_source.is_at_line(1, ')'),
            ),
        ]

    @staticmethod
    def cases_w_parentheses(expected_int: int) -> List[NSourceCase]:
        syntax = _ExprWithinParenthesesAbsStx(str(expected_int))
        tokens = syntax.tokenization()

        ret_val = []

        for layout_case in layout.STANDARD_LAYOUT_SPECS:
            source_str = tokens.layout(layout_case.value)
            for source_case in equivalent_source_variants__for_expr_parse__s__nsc(source_str):
                ret_val.append(
                    NSourceCase(
                        'layout={}, source={}'.format(layout_case.name, source_case.name),
                        source_case.source,
                        source_case.expectation
                    )
                )

        return ret_val


class TestFailureOfPlainParse(unittest.TestCase):
    SOURCE_STR_CASES = [
        NameAndValue(
            'wo parentheses',
            '',
        ),
        NameAndValue(
            'w parentheses',
            '( )',
        ),
    ]

    def test_parse_from_parse_source(self):
        parser = sut.OptionallySurroundedByParenthesesParser(_ParserThatRaisesException())
        for case in self.SOURCE_STR_CASES:
            parse_source = ParseSource(case.value)
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(parse_source)

    def test_parse_from_token_parser(self):
        parser = sut.OptionallySurroundedByParenthesesParser(_ParserThatRaisesException())
        for case in self.SOURCE_STR_CASES:
            token_parser = _token_parser_of(case.value)
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse_from_token_parser(token_parser)


class TestInvalidSyntaxForMissingEndParenthesis(unittest.TestCase):
    SOURCE_STR_CASES = [
        NameAndValue(
            'empty after int',
            '( 5',
        ),
        NameAndValue(
            'int instead of )',
            '( 5 7',
        ),
    ]

    def test_parse_from_parse_source(self):
        for case in self.SOURCE_STR_CASES:
            parse_source = ParseSource(case.value)
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    _SUT_PARSER_OF_INT.parse(parse_source)

    def test_parse_from_token_parser(self):
        for case in self.SOURCE_STR_CASES:
            token_parser = _token_parser_of(case.value)
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    _SUT_PARSER_OF_INT.parse_from_token_parser(token_parser)


class _ParserThatRaisesException(sut.Parser):
    def parse(self, source: ParseSource) -> PARSE_RESULT:
        raise SingleInstructionInvalidArgumentException('err msg')

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        raise SingleInstructionInvalidArgumentException('err msg')


class _ParserOfInt(ParserFromTokenParserBase[int]):
    def parse_from_token_parser(self, parser: TokenParser) -> int:
        parser.require_has_valid_head_token('INTEGER')
        int_token = parser.consume_mandatory_token('err msg format string')
        try:
            return int(int_token.string)
        except ValueError:
            raise SingleInstructionInvalidArgumentException('Not an int: ' + int_token.string)


def _check_parse_from_parse_source(put: unittest.TestCase,
                                   source: ParseSource,
                                   expected_parsed_value: int,
                                   expected_source_after_parse: Assertion[ParseSource]):
    # ACT #
    actual = _SUT_PARSER_OF_INT.parse(source)
    # ASSERT #
    put.assertEqual(expected_parsed_value,
                    actual,
                    'parsed value')
    expected_source_after_parse.apply_with_message(
        put,
        source,
        'source',
    )


def _check_parse_from_token_parser(put: unittest.TestCase,
                                   source: ParseSource,
                                   expected_parsed_value: int,
                                   expected_source_after_parse: Assertion[ParseSource]):
    with token_stream_parser.from_parse_source(source, False, False) as token_parser:
        # ACT #
        actual = _SUT_PARSER_OF_INT.parse_from_token_parser(token_parser)
    # ASSERT #
    put.assertEqual(expected_parsed_value,
                    actual,
                    'parsed value')
    expected_source_after_parse.apply_with_message(
        put,
        source,
        'source',
    )


class _ExprWithinParenthesesAbsStx(AbstractSyntax):
    def __init__(self, plain_expt: str):
        self._plain_expt = plain_expt

    def tokenization(self) -> TokenSequence:
        return TokenSequence.sequence([
            layout.OPTIONAL_NEW_LINE,
            '(',
            self._plain_expt,
            layout.OPTIONAL_NEW_LINE,
            ')',
        ])


def _token_parser_of(source: str) -> TokenParser:
    return TokenParser(TokenStream(source))


_SUT_PARSER_OF_INT = sut.OptionallySurroundedByParenthesesParser(_ParserOfInt())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
