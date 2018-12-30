import unittest

from typing import Iterable

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherResolverConstantTestImpl, \
    is_reference_to_string_matcher
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.instruction_test_configuration import \
    TestConfigurationForMatcher
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.instruction_test_configuration import \
    TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_validator import ValidatorThat, \
    pre_sds_validation_fails, post_sds_validation_fails, all_validation_passes
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    configuration = TestConfigurationForMatcher()

    test_cases = [
        ParseShouldFailWhenThereAreSuperfluousArguments,
        ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument,
        ValidationShouldFailIffItFailsForReferencedMatcher,
        ActualFileIsEmpty,
        ActualFileIsNonEmpty,

        ActualFileIsEmptyAfterTransformation,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


SYMBOL_FOR_EMPTINESS_MATCHER = NameAndValue(
    'SYMBOL_NAME',
    StringMatcherResolverConstantTestImpl(EmptinessStringMatcher(ExpectationType.POSITIVE))
)


class ParseShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {symbol_reference} superfluous-argument',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                         symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(
    TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {symbol_reference} <<MARKER',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                         symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name),
                    ['single line',
                     'MARKER'])
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ParseShouldFailWhenSymbolNameHasInvalidSyntax(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                         symbol_reference=symbol_reference_syntax_for_name(SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ValidationShouldFailIffItFailsForReferencedMatcher(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        validation_cases = [
            NEA('fail pre sds',
                expected=pre_sds_validation_fails(),
                actual=ValidatorThat(pre_sds_return_value='pre sds validation error'),
                ),
            NEA('fail post sds',
                expected=post_sds_validation_fails(),
                actual=ValidatorThat(post_setup_return_value='post sds validation error'),
                ),
            NEA('no failure',
                expected=all_validation_passes(),
                actual=ValidatorThat(),
                ),
        ]
        for validation_case in validation_cases:

            referenced_matcher = NameAndValue('REFERENCED_MATCHER',
                                              StringMatcherResolverConstantTestImpl(
                                                  EmptinessStringMatcher(ExpectationType.POSITIVE),
                                                  validator=validation_case.actual
                                              ))
            symbols = SymbolTable({
                referenced_matcher.name: container(referenced_matcher.value),
            })
            expected_symbol_references = asrt.matches_sequence([
                is_reference_to_string_matcher(referenced_matcher.name),
            ])

            for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
                with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                    self._check_with_source_variants(
                        self.configuration.arguments_for(
                            args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                                 maybe_with_transformer_option=maybe_with_transformer_option,
                                 maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                                 symbol_reference=referenced_matcher.name)),
                        model_construction.empty_model(),
                        self.configuration.arrangement_for_contents(
                            symbols=symbols),
                        Expectation(
                            main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                            symbol_usages=expected_symbol_references,
                            validation_pre_sds=validation_case.expected.pre_sds,
                            validation_post_sds=validation_case.expected.post_sds,
                        ),
                    )


class ActualFileIsEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
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
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                             symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                    model_construction.empty_model(),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                        symbols=symbols),
                    Expectation(
                        main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        symbol_usages=expected_symbol_references),
                )


class ActualFileIsNonEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
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
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                             symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                    model_construction.model_of('contents that makes the file non-empty'),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                        symbols=symbols),
                    Expectation(
                        main_result=self.maybe_not.fail__if_positive__pass_if_negative,
                        symbol_usages=expected_symbol_references),
                )


class ActualFileIsEmptyAfterTransformation(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         StringTransformerConstant(
                                             DeleteEverythingStringTransformer()))

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
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                     symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
            model_construction.model_of(original_file_contents),
            self.configuration.arrangement_for_contents(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols),
            Expectation(
                main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_references),
        )


class DeleteEverythingStringTransformer(StringTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda x: '', lines)
