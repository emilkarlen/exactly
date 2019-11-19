import unittest
from typing import List, Callable

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer as sut
from exactly_lib_test.symbol.data.test_resources.string_sdvs import StringSdvTestImpl
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import is_reference_to_data_type_symbol
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_sdvs
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as arg, \
    model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import quoting
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(Test),
        ReferencedSymbolsShouldBeReportedAndUsed(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


class TestInvalidSyntax(integration_check.TestCaseWithCheckMethods):
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


class Test(integration_check.TestCaseWithCheckMethods):
    def test_SHOULD_not_be_identity_transformer(self):
        # ARRANGE #
        arbitrary_string = 's'
        arguments = arg.syntax_for_replace_transformer(arbitrary_string,
                                                       arbitrary_string)
        # ACT & ASSERT #
        self._check_with_source_variants(
            Arguments(arguments),
            model_construction.arbitrary_model_constructor(),
            integration_check.Arrangement(),
            integration_check.Expectation(
                is_identity_transformer=asrt.equals(False),
            )
        )

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        def lines(pattern_matching_string: str) -> List[str]:
            return [
                'unidentified flying {}'.format(pattern_matching_string),
                '{} oriented'.format(pattern_matching_string),
                'I {}!'.format(pattern_matching_string),
            ]

        source_cases = [
            NEA('single word tokens',
                'transformer',
                'object',
                ),
            NEA('multi word tokens',
                quoting.surrounded_by_soft_quotes_str('t r a n s f o r m er'),
                quoting.surrounded_by_soft_quotes_str('o b j e c t'),
                ),
        ]
        # ACT & ASSERT #
        self._check_lines(lines, source_cases)

    def test_every_match_on_a_line_SHOULD_be_replaced(self):
        # ARRANGE #
        def lines(pattern_matching_string: str) -> List[str]:
            return [
                'we are {0} and they are {0} too'.format(pattern_matching_string),
            ]

        source_cases = [
            NEA('single word tokens',
                'here',
                'there',
                ),
            NEA('multi word tokens',
                quoting.surrounded_by_soft_quotes_str('h e r e'),
                quoting.surrounded_by_soft_quotes_str('t h e r e'),
                ),
        ]
        # ACT & ASSERT #
        self._check_lines(lines, source_cases)

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

        self._check_with_source_variants(
            Arguments(source),
            model_construction.of_lines(input_lines),
            integration_check.Arrangement(),
            integration_check.Expectation(
                main_result=asrt.on_transformed(list,
                                                asrt.equals(expected_lines))
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

        self._check_with_source_variants(
            Arguments(source),
            model_construction.of_lines(input_lines),
            integration_check.Arrangement(),
            integration_check.Expectation(
                main_result=asrt.on_transformed(list,
                                                asrt.equals(expected_lines))
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

                self._check_with_source_variants(
                    Arguments(source),
                    model_construction.of_lines(lines_for(source_case.actual)),
                    integration_check.Arrangement(),
                    integration_check.Expectation(
                        main_result=asrt.on_transformed(list,
                                                        asrt.equals(lines_for(source_case.expected)))
                    )
                )


class ReferencedSymbolsShouldBeReportedAndUsed(integration_check.TestCaseWithCheckMethods):
    def runTest(self):
        # ARRANGE #

        symbol_in_regex = NameAndValue('symbol_in_regex',
                                       'plain string pattern')
        symbol_in_replacement = NameAndValue('symbol_in_replacement',
                                             'the replacement')

        input_lines = [
            symbol_in_regex.value,
        ]
        expected_lines = [
            symbol_in_replacement.value,
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

                self._check_with_source_variants(
                    Arguments(source),
                    model_construction.of_lines(input_lines),
                    integration_check.Arrangement(
                        symbols=symbol_table_from_name_and_sdvs([
                            NameAndValue(symbol_in_regex.name,
                                         StringSdvTestImpl(symbol_in_regex.value)),
                            NameAndValue(symbol_in_replacement.name,
                                         StringSdvTestImpl(symbol_in_replacement.value)),
                        ]),
                    ),
                    integration_check.Expectation(
                        symbol_references=
                        asrt.matches_sequence([
                            is_reference_to_valid_regex_string_part(symbol_in_regex.name),
                            is_reference_to_data_type_symbol(symbol_in_replacement.name),
                        ]),
                        main_result=asrt.on_transformed(list,
                                                        asrt.equals(expected_lines)),
                    )
                )


class ValidationShouldFailWhenRegexIsInvalid(integration_check.TestCaseWithCheckMethods):
    def runTest(self):
        for regex_case in failing_regex_validation_cases():
            source = arg.syntax_for_replace_transformer(regex_case.regex_string,
                                                        'arbitrary_replacement')
            with self.subTest(regex_case.case_name):
                self._check_with_source_variants(
                    Arguments(source),
                    model_construction.arbitrary_model_constructor(),
                    integration_check.Arrangement(
                        symbols=symbol_table_from_name_and_sdvs(regex_case.symbols)
                    ),
                    integration_check.Expectation(
                        symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                        validation=regex_case.expectation
                    )
                )
