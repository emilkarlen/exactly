import unittest

from typing import Iterable

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import test_configuration as tc
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ParseShouldFailWhenThereAreSuperfluousArguments(),
        ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(),

        ActualFileIsEmpty(),
        ActualFileIsNonEmpty(),
        ActualFileIsEmptyAfterTransformation(),
    ])


class ParseShouldFailWhenThereAreSuperfluousArguments(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {empty} superfluous-argument',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(
    tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {empty} <<MARKER',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                    ['single line',
                     'MARKER'])
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ActualFileIsEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {empty}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_construction.empty_model(),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(main_result=maybe_not.pass__if_positive__fail__if_negative),
                )


class ActualFileIsNonEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {empty}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_construction.model_of('contents that makes the file non-empty'),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(main_result=maybe_not.fail__if_positive__pass_if_negative),
                )


class ActualFileIsEmptyAfterTransformation(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         StringTransformerConstant(
                                             DeleteEverythingStringTransformer()))

        original_file_contents = 'some\ntext'

        symbols = SymbolTable({
            named_transformer.name: container(named_transformer.value)
        })

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([expected_symbol_reference_to_transformer])

        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{transform_option} {the_transformer} {maybe_not} {empty}',
                     the_transformer=named_transformer.name,
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model_construction.model_of(original_file_contents),
            self.configuration.arrangement_for_contents(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols),
            Expectation(
                main_result=maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages),
        )


class DeleteEverythingStringTransformer(StringTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda x: '', lines)
