import unittest

from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.test_case_utils.string_transformer.impl.sequence import SequenceStringTransformer
from exactly_lib.type_system.logic.string_transformer import StringTransformerModel
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer, \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_wo_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as st_args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import StringTransformerTestImplBase
from exactly_lib_test.type_system.logic.test_resources.string_transformer_assertions import is_identity_transformer
from exactly_lib_test.type_system.logic.test_resources.string_transformers import MyNonIdentityTransformer, \
    MyToUppercaseTransformer, MyCountNumUppercaseCharactersTransformer


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
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines(initial_model_lines),
                    arrangement_wo_tcds(
                        SymbolContext.symbol_table_of_contexts([
                            StringTransformerSymbolContext.of_primitive(symbol.name, symbol.value)
                            for symbol in sequenced_transformer_symbols
                        ])
                    ),
                    expectation_of_successful_execution(
                        output_lines=expected_output_lines,
                        symbol_references=asrt.matches_sequence([
                            is_reference_to_string_transformer(symbol.name)
                            for symbol in sequenced_transformer_symbols
                        ]),
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
                        arrangement_wo_tcds(
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


class _AddLineTransformer(StringTransformerTestImplBase):
    def __init__(self, line_contents: str):
        self.line_to_add = line_contents + '\n'

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        for line in lines:
            yield line
        yield self.line_to_add


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
                SequenceStringTransformer([MyNonIdentityTransformer()]),
                False,
            ),
        ]
        for case_name, transformer, expected in cases:
            with self.subTest(case_name=case_name):
                self.assertEqual(expected,
                                 transformer.is_identity_transformer,
                                 'is_identity_transformation')

    def test_construct_and_get_transformers_list(self):
        # ARRANGE #
        t_1 = IdentityStringTransformer()
        t_2 = IdentityStringTransformer()
        transformers_given_to_constructor = [t_1, t_2]

        # ACT #

        sequence = SequenceStringTransformer(transformers_given_to_constructor)
        transformers_from_sequence = sequence.transformers

        # ASSERT #

        self.assertEqual(transformers_given_to_constructor,
                         list(transformers_from_sequence))

    def test_WHEN_sequence_of_transformers_is_empty_THEN_output_SHOULD_be_equal_to_input(self):
        # ARRANGE #
        sequence = SequenceStringTransformer([])

        input_lines = ['first',
                       'second',
                       'third']
        input_iter = iter(input_lines)
        # ACT #
        output = sequence.transform(input_iter)
        # ASSERT #
        output_lines = list(output)

        self.assertEqual(input_lines,
                         output_lines)

    def test_WHEN_single_transformer_THEN_sequence_SHOULD_be_identical_to_the_single_transformer(self):
        # ARRANGE #

        to_upper_t = MyToUppercaseTransformer()

        sequence = SequenceStringTransformer([to_upper_t])

        input_lines = ['first',
                       'second',
                       'third']

        # ACT #

        actual = sequence.transform(iter(input_lines))

        # ASSERT #

        expected_output_lines = ['FIRST',
                                 'SECOND',
                                 'THIRD']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)

    def test_WHEN_multiple_transformers_THEN_transformers_SHOULD_be_chained(self):
        # ARRANGE #

        to_upper_t = MyToUppercaseTransformer()
        count_num_upper = MyCountNumUppercaseCharactersTransformer()

        sequence = SequenceStringTransformer([to_upper_t,
                                              count_num_upper])

        input_lines = ['this is',
                       'the',
                       'input']

        # ACT #

        actual = sequence.transform(iter(input_lines))

        # ASSERT #

        expected_output_lines = ['6',
                                 '3',
                                 '5']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)
