import unittest

from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Arrangement, Expectation, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check, test_configuration
from exactly_lib_test.test_case_utils.string_matcher.test_resources import test_configuration as tc
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    every_line_empty


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ActualFileIsEmpty(),
        ActualFileIsNonEmpty(),
        ActualFileIsEmptyAfterTransformation(),
        StringTransformerShouldBeValidated(),
    ])


class ActualFileIsEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    test_configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {empty}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    integration_check.empty_model(),
                    arrangement_w_tcds(
                        post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(
                        execution=ExecutionExpectation(
                            main_result=maybe_not.pass__if_positive__fail__if_negative
                        ),
                    ),
                )


class ActualFileIsNonEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    test_configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {empty}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    integration_check.model_of('contents that makes the file non-empty'),
                    arrangement_w_tcds(
                        post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(
                        execution=ExecutionExpectation(
                            main_result=maybe_not.fail__if_positive__pass_if_negative
                        ),
                    ),
                )


class ActualFileIsEmptyAfterTransformation(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #
        named_transformer = StringTransformerSymbolContext.of_primitive(
            'the_transformer',
            every_line_empty()
        )

        original_file_contents = 'some\ntext'

        symbols = SymbolTable({
            named_transformer.name: named_transformer.symbol_table_container
        })

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([expected_symbol_reference_to_transformer])

        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{transform_option} {the_transformer} {maybe_not} {empty}',
                     the_transformer=named_transformer.name,
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            integration_check.model_of(original_file_contents),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols),
            Expectation(
                ParseExpectation(
                    symbol_references=expected_symbol_usages),
                ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative,
                ),
            )
        )


class StringTransformerShouldBeValidated(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for case in failing_validation_cases():
            with self.subTest(validation_case=case.name):
                self._check(
                    test_configuration.source_for(
                        args('{transformer_option} {maybe_not} {empty}',
                             transformer_option=case.value.transformer_arguments_string,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    integration_check.empty_model(),
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
