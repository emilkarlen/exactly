import unittest

import re

from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.test_case_utils.string_transformer.impl import replace as sut
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import is_reference_to_data_type_symbol
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_resolvers
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as arg
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.model_construction import arbitrary_model
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test),
        ReferencedSymbolsShouldBeReported(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


class Test(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.ReplaceStringTransformer(re.compile('object'),
                                                   'transformer')
        self.assertFalse(transformer.is_identity_transformer)

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        input_lines = [
            'unidentified flying object',
            'object oriented',
            'I object!',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ReplaceStringTransformer(re.compile('object'),
                                                   'transformer')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        expected_lines = [
            'unidentified flying transformer',
            'transformer oriented',
            'I transformer!',
        ]

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_every_match_on_a_line_SHOULD_be_replaced(self):
        # ARRANGE #
        input_lines = [
            'we are here and they are here too',
            'here I am',
            'I am here',
        ]
        expected_lines = [
            'we are there and they are there too',
            'there I am',
            'I am there',
        ]
        input_lines_iter = iter(input_lines)
        transformer = sut.ReplaceStringTransformer(re.compile('here'),
                                                   'there')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_regular_expression_SHOULD_be_matched(self):
        # ARRANGE #
        lines = [
            'Exactly',
        ]
        expected_lines = [
            'is what I want',
        ]
        input_lines_iter = iter(lines)
        transformer = sut.ReplaceStringTransformer(re.compile('[E][x][a][c][t][l][y]'),
                                                   'is what I want')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_newline_ends_SHOULD_not_be_included_in_the_transformation(self):
        # ARRANGE #
        lines = [
            ' 1 2 \n',
            ' 3 4 ',
        ]
        expected_lines = [
            '12\n',
            '34',
        ]
        input_lines_iter = iter(lines)
        transformer = sut.ReplaceStringTransformer(re.compile('\s'),
                                                   '')
        # ACT #

        actual = transformer.transform(input_lines_iter)

        # ASSERT #

        actual_lines = list(actual)

        self.assertEqual(expected_lines,
                         actual_lines)


class ReferencedSymbolsShouldBeReported(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        symbol_in_regex = SymbolWithReferenceSyntax('symbol_in_regex')
        symbol_in_replacement = SymbolWithReferenceSyntax('symbol_in_replacement')

        arguments_string = arg.syntax_for_replace_transformer(str(symbol_in_regex), str(symbol_in_replacement))
        arguments = Arguments(arguments_string)
        source = remaining_source(arguments_string)

        references_expectation = asrt.matches_sequence([
            is_reference_to_valid_regex_string_part(symbol_in_regex.name),
            is_reference_to_data_type_symbol(symbol_in_replacement.name),
        ])

        # ACT #

        for source in equivalent_source_variants__with_source_check__for_expression_parser(self, arguments):
            actual = parse_string_transformer.parser().parse(source)

            # ASSERT #

            actual_references = actual.references

            references_expectation.apply_without_message(self, actual_references)


class ValidationShouldFailWhenRegexIsInvalid(unittest.TestCase):
    def runTest(self):
        for regex_case in failing_regex_validation_cases():
            source = arg.syntax_for_replace_transformer(regex_case.regex_string,
                                                        'arbitrary replacement')
            with self.subTest(regex_case.case_name):
                integration_check.check(
                    self,
                    remaining_source(source),
                    arbitrary_model(),
                    integration_check.Arrangement(
                        symbols=symbol_table_from_name_and_resolvers(regex_case.symbols)
                    ),
                    integration_check.Expectation(
                        symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                        validation=regex_case.expectation
                    )
                )
