import unittest

from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.test_case_utils.string_transformer.impl.sequence import SequenceStringTransformer
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as st_args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution
from exactly_lib_test.test_case_utils.test_resources import string_models
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformer_assertions import \
    is_identity_transformer
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    arbitrary_non_identity, to_uppercase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPrimitiveValue),
        ResultShouldBeCompositionOfSequencedTransformers(),
        ValidatorShouldValidateSequencedTransformers(),
    ])


class ResultShouldBeCompositionOfSequencedTransformers(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        symbol_1 = NameAndValue('symbol_1_name',
                                'added by 1st transformer')
        symbol_2 = NameAndValue('symbol_2_name',
                                'added by 2nd transformer')
        symbol_3 = NameAndValue('symbol_3_name',
                                'added by 3rd transformer')

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
                symbol.value + '\n'
                for symbol in sequenced_transformer_symbols
            ]

            symbol_contexts = [
                StringTransformerSymbolContext.of_primitive(symbol.name,
                                                            string_transformers.add_line(symbol.value))
                for symbol in sequenced_transformer_symbols
            ]
            # ACT & ASSERT #

            with self.subTest(case.name):
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines(initial_model_lines),
                    arrangement_w_tcds(
                        symbols=SymbolContext.symbol_table_of_contexts(symbol_contexts)
                    ),
                    expectation_of_successful_execution(
                        output_lines=expected_output_lines,
                        symbol_references=SymbolContext.references_assertion_of_contexts(symbol_contexts),
                        is_identity_transformer=False,
                    )
                )


class ValidatorShouldValidateSequencedTransformers(unittest.TestCase):
    def runTest(self):
        successful_transformer = StringTransformerSymbolContext.of_identity('successful_transformer')
        for case in validation_cases.failing_validation_cases('failing_transformer'):
            failing_symbol_context = case.value.symbol_context

            symbols = SymbolContext.symbol_table_of_contexts([
                failing_symbol_context,
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
                expected_symbol_references = asrt.matches_sequence([
                    is_reference_to_string_transformer(symbol_name)
                    for symbol_name in order_case.value
                ])

                with self.subTest(validation_case=case.name,
                                  order_case=order_case.name):
                    integration_check.CHECKER.check__w_source_variants(
                        self,
                        Arguments(arguments),
                        model_construction.of_lines([]),
                        arrangement_w_tcds(
                            symbols=symbols
                        ),
                        logic_integration_check.Expectation(
                            logic_integration_check.ParseExpectation(
                                symbol_references=expected_symbol_references
                            ),
                            logic_integration_check.ExecutionExpectation(
                                validation=case.value.expectation,
                            ),
                            is_identity_transformer(False),
                        )
                    )


class TestPrimitiveValue(unittest.TestCase):
    def test_SHOULD_is_identity_transformer(self):
        cases = [
            (
                'empty list of transformers',
                SequenceStringTransformer([]),
                True,
            ),
            (
                'single identity transformer',
                SequenceStringTransformer([IdentityStringTransformer()]),
                True,
            ),
            (
                'multiple identity transformers',
                SequenceStringTransformer([IdentityStringTransformer(),
                                           IdentityStringTransformer()]),
                True,
            ),
            (
                'non-identity transformer',
                SequenceStringTransformer([arbitrary_non_identity()]),
                False,
            ),
        ]
        for case_name, transformer, expected in cases:
            with self.subTest(case_name=case_name):
                self.assertEqual(expected,
                                 transformer.is_identity_transformer,
                                 'is_identity_transformation')

    def test_WHEN_sequence_of_transformers_is_empty_THEN_output_SHOULD_be_equal_to_input(self):
        # ARRANGE #
        transformer = SequenceStringTransformer([])

        input_lines = ['first',
                       'second',
                       'third']
        model = string_models.of_lines(input_lines)
        # ACT #
        actual = transformer.transform(model)
        # ASSERT #
        actual_lines = string_models.as_lines_list(actual)

        self.assertEqual(input_lines,
                         actual_lines)

    def test_WHEN_single_transformer_THEN_sequence_SHOULD_be_identical_to_the_single_transformer(self):
        # ARRANGE #

        to_upper_t = string_transformers.to_uppercase()

        transformer = SequenceStringTransformer([to_upper_t])

        input_lines = ['first',
                       'second',
                       'third']
        model = string_models.of_lines(input_lines)

        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        expected_output_lines = ['FIRST',
                                 'SECOND',
                                 'THIRD']

        actual_lines = string_models.as_lines_list(actual)

        self.assertEqual(expected_output_lines,
                         actual_lines)

    def test_WHEN_multiple_transformers_THEN_transformers_SHOULD_be_chained(self):
        # ARRANGE #

        to_upper_t = to_uppercase()
        count_num_upper = string_transformers.count_num_uppercase_characters()

        transformer = SequenceStringTransformer([to_upper_t,
                                                 count_num_upper])

        input_lines = ['this is',
                       'the',
                       'input']
        model = string_models.of_lines(input_lines)

        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        expected_output_lines = ['6',
                                 '3',
                                 '5']

        actual_lines = string_models.as_lines_list(actual)

        self.assertEqual(expected_output_lines,
                         actual_lines)
