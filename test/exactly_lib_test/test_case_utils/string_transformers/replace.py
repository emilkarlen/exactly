import unittest
from typing import List, Callable, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import \
    arrangement_wo_tcds, Expectation, ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as arg, \
    model_construction, integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import StExpectation
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformer_assertions import \
    is_identity_transformer
from exactly_lib_test.util.test_resources import quoting
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(Test),
        ReferencedSymbolsShouldBeReportedAndUsed(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


class TransformationCase:
    def __init__(self,
                 name: str,
                 regex: str,
                 replacement: str):
        self.name = name
        self.regex = regex
        self.replacement = replacement


class TestInvalidSyntax(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'no arguments',
                arg.syntax_for_replace_transformer__custom(Arguments.empty()),
            ),
            NameAndValue(
                'single REGEX argument (missing REPLACEMENT)',
                arg.syntax_for_replace_transformer__custom(Arguments('regex')),
            ),
            NameAndValue(
                'single REGEX argument (missing REPLACEMENT), but it appears on the following line',
                arg.syntax_for_replace_transformer__custom(Arguments('regex',
                                                                     ['replacement'])),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parser().parse(case.value.as_remaining_source)


class Test(unittest.TestCase):
    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        def lines(pattern_matching_string: str) -> List[str]:
            return [
                'unidentified flying {}'.format(pattern_matching_string),
                '{} oriented'.format(pattern_matching_string),
                'I {}!'.format(pattern_matching_string),
            ]

        source_cases = [
            TransformationCase('single word tokens',
                               'transformer',
                               'object',
                               ),
            TransformationCase('multi word tokens',
                               quoting.surrounded_by_soft_quotes_str('t r a n s f o r m er'),
                               quoting.surrounded_by_soft_quotes_str('o b j e c t'),
                               ),
        ]
        # ACT & ASSERT #
        self._check_lines_for_constant_regex(lines, source_cases)

    def test_every_match_on_a_line_SHOULD_be_replaced(self):
        # ARRANGE #
        def lines(pattern_matching_string: str) -> List[str]:
            return [
                'we are {0} and they are {0} too'.format(pattern_matching_string),
            ]

        source_cases = [
            TransformationCase('single word tokens',
                               'here',
                               'there',
                               ),
            TransformationCase('multi word tokens',
                               quoting.surrounded_by_soft_quotes_str('h e r e'),
                               quoting.surrounded_by_soft_quotes_str('t h e r e'),
                               ),
        ]
        # ACT & ASSERT #
        self._check_lines_for_constant_regex(lines, source_cases)

    def test_regular_expression_SHOULD_be_matched(self):
        # ARRANGE #
        input_lines = [
            'Exactly',
        ]
        expected_lines = [
            'is what I want',
        ]

        source = arg.syntax_for_replace_transformer('[E][x][a][c][t][l][y]',
                                                    '"is what I want"')

        # ACT & ASSERT #

        integration_check.CHECKER.check__w_source_variants(
            self,
            Arguments(source),
            model_construction.of_lines(input_lines),
            arrangement_wo_tcds(),
            expectation_of_successful_replace_execution(
                output_lines=expected_lines
            )
        )

    def test_newline_ends_SHOULD_not_be_included_in_the_transformation(self):
        # ARRANGE #
        input_lines = [
            ' 1 2 \n',
            ' 3 4 ',
        ]
        expected_lines = [
            '12\n',
            '34',
        ]

        source = arg.syntax_for_replace_transformer(str(surrounded_by_hard_quotes('\\s')),
                                                    '""')

        # ACT & ASSERT #

        integration_check.CHECKER.check__w_source_variants(
            self,
            Arguments(source),
            model_construction.of_lines(input_lines),
            arrangement_wo_tcds(),
            expectation_of_successful_replace_execution(
                output_lines=expected_lines
            )
        )

    def _check_lines(self,
                     lines_for: Callable[[str], List[str]],
                     source_cases: List[NEA[str, str]]):
        for source_case in source_cases:
            source = arg.syntax_for_replace_transformer(source_case.actual,
                                                        source_case.expected)
            with self.subTest(source_case.name):
                # ACT & ASSERT #

                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_construction.of_lines(lines_for(source_case.actual)),
                    arrangement_wo_tcds,
                    expectation_of_successful_replace_execution(
                        output_lines=source_case.expected
                    )
                )

    def _check_lines_for_constant_regex(self,
                                        lines_for: Callable[[str], List[str]],
                                        source_cases: List[TransformationCase]):
        for source_case in source_cases:
            source = arg.syntax_for_replace_transformer(source_case.regex,
                                                        source_case.replacement)
            with self.subTest(source_case.name):
                # ACT & ASSERT #

                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_construction.of_lines(lines_for(source_case.regex)),
                    arrangement_wo_tcds(),
                    Expectation(
                        ParseExpectation(
                            symbol_references=asrt.is_empty_sequence,
                        ),
                        ExecutionExpectation(
                            main_result=asrt.on_transformed(list,
                                                            asrt.equals(lines_for(source_case.replacement)))
                        )
                    )
                )


class ReferencedSymbolsShouldBeReportedAndUsed(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        symbol_in_regex = StringConstantSymbolContext('symbol_in_regex',
                                                      'plain string pattern')
        symbol_in_replacement = StringConstantSymbolContext('symbol_in_replacement',
                                                            'the replacement')

        input_lines = [
            symbol_in_regex.str_value,
        ]
        expected_lines = [
            symbol_in_replacement.str_value,
        ]
        quoting_cases = [
            NameAndValue('unquoted', lambda x: x),
            NameAndValue('soft quoted', quoting.surrounded_by_soft_quotes_str),
        ]
        for quoting_case in quoting_cases:
            source = arg.syntax_for_replace_transformer(
                quoting_case.value(symbol_reference_syntax_for_name(symbol_in_regex.name)),
                symbol_reference_syntax_for_name(symbol_in_replacement.name),
            )

            with self.subTest(quoting_case.name):
                # ACT & ASSERT #

                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_construction.of_lines(input_lines),
                    arrangement_wo_tcds(
                        symbols=SymbolContext.symbol_table_of_contexts([
                            symbol_in_regex,
                            symbol_in_replacement,
                        ]),
                    ),
                    expectation_of_successful_replace_execution(
                        symbol_references=
                        asrt.matches_sequence([
                            is_reference_to_valid_regex_string_part(symbol_in_regex.name),
                            symbol_in_replacement.reference_assertion__any_data_type,
                        ]),
                        output_lines=expected_lines,
                    )
                )


class ValidationShouldFailWhenRegexIsInvalid(unittest.TestCase):
    def runTest(self):
        for regex_case in failing_regex_validation_cases():
            source = arg.syntax_for_replace_transformer(regex_case.regex_string,
                                                        'arbitrary_replacement')
            with self.subTest(regex_case.case_name):
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_construction.arbitrary_model_constructor(),
                    arrangement_wo_tcds(
                        symbols=regex_case.symbol_table
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                        ),
                        ExecutionExpectation(
                            validation=regex_case.expectation
                        ),
                        is_identity_transformer(False),
                    )
                )


def expectation_of_successful_replace_execution(
        output_lines: List[str],
        symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
) -> StExpectation:
    return integration_check.expectation_of_successful_execution(
        output_lines,
        symbol_references,
        False,
    )
