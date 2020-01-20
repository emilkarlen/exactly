import unittest

from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__ref
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_matcher.test_resources import contents_transformation, integration_check, \
    arguments_building2 as args2
from exactly_lib_test.test_case_utils.string_matcher.test_resources import \
    validation_cases as string_matcher_failing_validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources import validation_cases \
    as string_transformer_failing_validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformers import \
    StringTransformerThatMustNotBeUsedTestImpl
from exactly_lib_test.test_resources.test_utils import NExArr, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import DeleteEverythingTransformer
from exactly_lib_test.type_system.logic.test_resources import string_transformers
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValidationShouldFailWhenValidationOfStringMatcherFails(),
        TestValidationShouldFailWhenValidationOfStringTransformerFails(),
        TestWhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(),
        unittest.makeSuite(TestWithBinaryOperators),
    ])


_TRANSFORMER_SYMBOL_NAME = 'the_transformer'


class TestWhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        original_model_contents = 'some text'
        expected_model_contents = original_model_contents.upper()

        cases = [
            NEA(
                'transformation that makes matcher match',
                True,
                string_transformers.MyToUppercaseTransformer(),
            ),
            NEA(
                'transformation that makes matcher NOT match',
                False,
                DeleteEverythingTransformer(),
            ),
        ]

        # ACT & ASSERT #

        integration_check.CHECKER.check_multi_execution(
            self,
            args2.Transformed(
                _TRANSFORMER_SYMBOL_NAME,
                args2.Equals(surrounded_by_hard_quotes_str(expected_model_contents))
            ).as_arguments,
            asrt.matches_singleton_sequence(
                is_reference_to_string_transformer__ref(_TRANSFORMER_SYMBOL_NAME)
            ),
            integration_check.model_of(original_model_contents),
            [
                NExArr(
                    case.name,
                    ExecutionExpectation(
                        main_result=asrt_matching_result.matches_value(case.expected),
                    ),
                    arrangement_w_tcds(
                        symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                            _TRANSFORMER_SYMBOL_NAME: StringTransformerSdvConstant(case.actual)
                        }),
                    )
                )
                for case in cases
            ],
        )


class TestValidationShouldFailWhenValidationOfStringMatcherFails(unittest.TestCase):
    def runTest(self):
        string_transformer = NameAndValue(
            'the_string_transformer',
            symbol_utils.container(
                StringTransformerSdvConstant(StringTransformerThatMustNotBeUsedTestImpl())
            )
        )
        for case in string_matcher_failing_validation_cases.failing_validation_cases():
            with self.subTest(validation_case=case.name):
                symbol_context = case.value.symbol_context
                integration_check.CHECKER.check_with_source_variants(
                    self,
                    args2.Transformed(
                        string_transformer.name,
                        args2.SymbolReference(symbol_context.name)
                    ).as_arguments,
                    integration_check.model_that_must_not_be_used,
                    Arrangement(
                        symbols=SymbolTable({
                            string_transformer.name: string_transformer.value,
                            symbol_context.name: symbol_context.symbol_table_container,
                        })
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=asrt.matches_sequence([
                                is_reference_to_string_transformer__ref(string_transformer.name),
                                symbol_context.reference_assertion,
                            ]),
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class TestValidationShouldFailWhenValidationOfStringTransformerFails(unittest.TestCase):
    def runTest(self):
        for case in string_transformer_failing_validation_cases.failing_validation_cases():
            with self.subTest(validation_case=case.name):
                integration_check.CHECKER.check_with_source_variants(
                    self,
                    args2.Transformed(
                        case.value.symbol_context.name,
                        args2.Empty()
                    ).as_arguments,
                    integration_check.model_that_must_not_be_used,
                    Arrangement(
                        symbols=case.value.symbol_context.symbol_table
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.value.symbol_context.references_assertion,
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class TestWithBinaryOperators(unittest.TestCase):
    def test_transformation_SHOULD_apply_to_all_operands_if_matcher_is_binary_operator_expression(self):
        to_upper_transformer = NameAndValue(
            'the_to_upper_transformer',
            StringTransformerSdvConstant(string_transformers.MyToUppercaseTransformer())
        )

        model = contents_transformation.TransformedContentsSetup(
            original='text',
            transformed='TEXT',
        )

        integration_check.CHECKER.check_with_source_variants(
            self,
            args2.Transformed(
                to_upper_transformer.name,
                args2.Parenthesis(
                    args2.conjunction([
                        args2.Equals(model.transformed),
                        args2.Equals(model.original),
                    ])
                )
            ).as_arguments,
            integration_check.model_of(model.original),
            arrangement_w_tcds(
                symbols=symbol_utils.symbol_table_from_name_and_sdvs([to_upper_transformer])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        is_reference_to_string_transformer__ref(to_upper_transformer.name)
                    )
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(False)
                )
            )
        )

    def test_transformation_SHOULD_apply_only_to_matcher_argument(self):
        to_upper_transformer = NameAndValue(
            'the_to_upper_transformer',
            StringTransformerSdvConstant(string_transformers.MyToUppercaseTransformer())
        )

        model = contents_transformation.TransformedContentsSetup(
            original='text',
            transformed='TEXT',
        )

        integration_check.CHECKER.check_with_source_variants(
            self,
            args2.conjunction([
                args2.Parenthesis(
                    args2.Transformed(
                        to_upper_transformer.name,
                        args2.Equals(model.transformed)
                    ),
                ),
                args2.Equals(model.original),
            ]).as_arguments,
            integration_check.model_of(model.original),
            arrangement_w_tcds(
                symbols=symbol_utils.symbol_table_from_name_and_sdvs([to_upper_transformer])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        is_reference_to_string_transformer__ref(to_upper_transformer.name)
                    )
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                )
            )
        )

    def test_transformation_SHOULD_2(self):
        to_upper_transformer = NameAndValue(
            'the_to_upper_transformer',
            StringTransformerSdvConstant(string_transformers.MyToUppercaseTransformer())
        )

        count_num_upper_characters_transformer = NameAndValue(
            'the_count_num_upper_transformer',
            StringTransformerSdvConstant(string_transformers.MyCountNumUppercaseCharactersTransformer())
        )

        model__original = 'text'
        model__upper = model__original.upper()
        model_num_upper_chars = str(len(model__upper))

        integration_check.CHECKER.check_with_source_variants(
            self,
            args2.Transformed(
                to_upper_transformer.name,
                args2.Parenthesis(
                    args2.conjunction([
                        args2.Parenthesis(
                            args2.Transformed(
                                count_num_upper_characters_transformer.name,
                                args2.Equals(model_num_upper_chars),
                            )
                        ),
                        args2.Equals(model__upper),
                    ])
                )
            ).as_arguments,
            integration_check.model_of(model__original),
            arrangement_w_tcds(
                symbols=symbol_utils.symbol_table_from_name_and_sdvs([
                    to_upper_transformer,
                    count_num_upper_characters_transformer,
                ])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_string_transformer__ref(to_upper_transformer.name),
                        is_reference_to_string_transformer__ref(count_num_upper_characters_transformer.name),
                    ]
                    )
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                )
            )
        )