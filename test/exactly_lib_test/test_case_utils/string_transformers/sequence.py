import itertools
import unittest

from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.string_transformer import StringTransformerModel, \
    IdentityStringTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__ref
from exactly_lib_test.symbol.test_resources.symbol_utils import container, symbol_table_from_name_and_resolvers
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as st_args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_assertions as asrt_model
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import Arrangement, \
    Expectation
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import StringTransformerTestImplBase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ResultShouldBeCompositionOfSequencedTransformers(),
        SymbolReferencesShouldBeReportedForEverySequencedTransformer(),
        ValidatorShouldValidateSequencedTransformers(),
    ])


class ResultShouldBeCompositionOfSequencedTransformers(integration_check.TestCaseWithCheckMethods):
    def runTest(self):
        # ARRANGE #
        symbol_1 = NameAndValue('symbol_1_name',
                                _AddLineTransformer('added by 1st transformer'))
        symbol_2 = NameAndValue('symbol_2_name',
                                _AddLineTransformer('added by 2nd transformer'))
        symbol_3 = NameAndValue('symbol_3_name',
                                _AddLineTransformer('added by 3rd transformer'))

        cases = [
            NameAndValue('2 transformers',
                         [
                             symbol_1,
                             symbol_2,
                         ]
                         ),
            NameAndValue('3 transformers',
                         [
                             symbol_1,
                             symbol_2,
                             symbol_3,
                         ]
                         ),
        ]
        for case in cases:
            sequenced_transformer_symbols = case.value

            arguments = st_args.syntax_for_sequence_of_transformers([
                symbol.name
                for symbol in sequenced_transformer_symbols
            ])

            initial_line = 'initial line\n'
            initial_model_lines = [initial_line]

            expected_output_lines = [initial_line] + [
                symbol.value.line_to_add
                for symbol in sequenced_transformer_symbols
            ]

            # ACT & ASSERT #

            with self.subTest(case.name):
                self._check_with_source_variants(
                    Arguments(arguments),
                    model_construction.of_lines(initial_model_lines),
                    Arrangement(
                        SymbolTable({
                            symbol.name: container(StringTransformerConstant(symbol.value))
                            for symbol in sequenced_transformer_symbols
                        })
                    ),
                    Expectation(
                        main_result=asrt_model.model_as_list_matches(asrt.equals(expected_output_lines)),
                        symbol_references=asrt.matches_sequence([
                            is_reference_to_string_transformer__ref(symbol.name)
                            for symbol in sequenced_transformer_symbols
                        ]),
                    )
                )


class SymbolReferencesShouldBeReportedForEverySequencedTransformer(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        transformer_symbols = ['st1', 'st2', 'st3']

        expected_references = asrt.matches_sequence([
            is_reference_to_string_transformer__ref(transformer)
            for transformer in transformer_symbols
        ])

        arguments = st_args.syntax_for_sequence_of_transformers([
            transformer
            for transformer in transformer_symbols
        ])

        parser = parse_string_transformer.parser()

        # ACT #

        actual = parser.parse(remaining_source(arguments))

        # ASSERT #

        self.assertIsInstance(actual, StringTransformerResolver)

        actual_references = actual.references

        expected_references.apply(self, actual_references)


class ValidatorShouldValidateSequencedTransformers(integration_check.TestCaseWithCheckMethods):
    def runTest(self):
        successful_transformer = NameAndValue(
            'successful_transformer',
            StringTransformerConstant(IdentityStringTransformer())
        )
        for case in validation_cases.failing_validation_cases('failing_transformer'):
            failing_symbol_context = case.value.symbol_context

            symbols = symbol_table_from_name_and_resolvers([
                failing_symbol_context.name_and_resolver,
                successful_transformer,
            ])

            order_cases = [
                NameAndValue('1st transformer fails',
                             [failing_symbol_context.name,
                              successful_transformer.name]
                             ),
                NameAndValue('2nd transformer fails',
                             [successful_transformer.name,
                              failing_symbol_context.name]
                             ),
            ]
            for order_case in order_cases:
                arguments = st_args.syntax_for_sequence_of_transformers(order_case.value)

                with self.subTest(validation_case=case.name,
                                  order_case=order_case.name):
                    self._check(
                        remaining_source(arguments),
                        [],
                        Arrangement(
                            symbols=symbols
                        ),
                        Expectation(
                            validation=case.value.expectation,
                            symbol_references=asrt.anything_goes()
                        )
                    )


class _AddLineTransformer(StringTransformerTestImplBase):
    def __init__(self, line_contents: str):
        self.line_to_add = line_contents + '\n'

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return itertools.chain.from_iterable([
            lines,
            [self.line_to_add]
        ])
