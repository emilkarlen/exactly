import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.string_matcher import string_matcher_sdv_constant_test_impl, \
    is_reference_to_string_matcher
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import test_configuration as tc
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.validation_cases import failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation, expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import EveryLineEmptyStringTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ActualFileIsEmpty(),
        ActualFileIsNonEmpty(),
        ActualFileIsEmptyAfterTransformation(),
        ReferencedMatcherShouldBeValidated(),
    ])


SYMBOL_FOR_EMPTINESS_MATCHER = NameAndValue(
    'SYMBOL_NAME',
    string_matcher_sdv_constant_test_impl(EmptinessStringMatcher(ExpectationType.POSITIVE))
)


class ParseShouldFailWhenSymbolNameHasInvalidSyntax(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                         symbol_reference=symbol_reference_syntax_for_name(SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ReferencedMatcherShouldBeValidated(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for case in failing_validation_cases():
            with self.subTest(validation_case=case.name):
                self._check(
                    self.configuration.source_for(
                        args('{maybe_not} {symbol_reference}',
                             symbol_reference=case.value.symbol_context.name,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_construction.empty_model(),
                    self.configuration.arrangement_for_contents(
                        symbols=case.value.symbol_context.symbol_table
                    ),
                    expectation(
                        validation=case.value.expectation,
                        symbol_references=case.value.symbol_context.references_assertion
                    ),
                )


class ActualFileIsEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        symbols = SymbolTable({
            SYMBOL_FOR_EMPTINESS_MATCHER.name: container(SYMBOL_FOR_EMPTINESS_MATCHER.value),
        })
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_matcher(SYMBOL_FOR_EMPTINESS_MATCHER.name),
        ])

        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                             symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                    model_construction.empty_model(),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                        symbols=symbols),
                    Expectation(
                        main_result=maybe_not.pass__if_positive__fail__if_negative,
                        symbol_usages=expected_symbol_references),
                )


class ActualFileIsNonEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        symbols = SymbolTable({
            SYMBOL_FOR_EMPTINESS_MATCHER.name: container(SYMBOL_FOR_EMPTINESS_MATCHER.value),
        })
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_matcher(SYMBOL_FOR_EMPTINESS_MATCHER.name),
        ])

        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                             symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                    model_construction.model_of('contents that makes the file non-empty'),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                        symbols=symbols),
                    Expectation(
                        main_result=maybe_not.fail__if_positive__pass_if_negative,
                        symbol_usages=expected_symbol_references),
                )


class ActualFileIsEmptyAfterTransformation(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         StringTransformerSdvConstant(
                                             EveryLineEmptyStringTransformer()))

        original_file_contents = 'some\ntext'

        symbols = SymbolTable({
            named_transformer.name: container(named_transformer.value),
            SYMBOL_FOR_EMPTINESS_MATCHER.name: container(SYMBOL_FOR_EMPTINESS_MATCHER.value),
        })

        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(named_transformer.name),
            is_reference_to_string_matcher(SYMBOL_FOR_EMPTINESS_MATCHER.name),
        ])

        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{transform_option} {the_transformer} {maybe_not} {symbol_reference}',
                     the_transformer=named_transformer.name,
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                     symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
            model_construction.model_of(original_file_contents),
            self.configuration.arrangement_for_contents(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols),
            Expectation(
                main_result=maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_references),
        )
