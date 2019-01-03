import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements, \
    here_document_as_elements
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import test_configuration as tc
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES, TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.integration_check import Expectation, \
    arbitrary_validation_failure
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ParseShouldFailWhenThereAreSuperfluousArguments(),
        ParseShouldFailWhenRegexArgumentIsMissing(),
        ValidationShouldFailPreWhenHardCodedRegexIsInvalid(),

        FullMatchSingleLineWoNewline(),
        PartialMatchSingleLineWoNewline(),

        FullMatchSingleLineWNewline(),
        ActualContainsExtraLineAfterMatchingLines(),
    ])


class ParseShouldFailWhenThereAreSuperfluousArguments(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {matches} regex superfluous-argument',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ValidationShouldFailPreWhenHardCodedRegexIsInvalid(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matches} **',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_construction.empty_model(),
                    self.configuration.arrangement_for_contents(),
                    Expectation(
                        validation_pre_sds=arbitrary_validation_failure())
                )


class ParseShouldFailWhenRegexArgumentIsMissing(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {matches}',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class FullMatchSingleLineWoNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = '123'
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matches} 1.3',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_construction.model_of(actual_contents),
                    self.configuration.arrangement_for_contents(),
                    Expectation(main_result=maybe_not.pass__if_positive__fail__if_negative),
                )


class PartialMatchSingleLineWoNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = '01234'
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matches} 1.3',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_construction.model_of(actual_contents),
                    self.configuration.arrangement_for_contents(),
                    Expectation(main_result=maybe_not.fail__if_positive__pass_if_negative),
                )


class FullMatchSingleLineWNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = lines_content(['123'])
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            with self.subTest(maybe_with_transformer_option=transformer_option_arguments):
                argument_elements = ArgumentElements(transformer_option_arguments +
                                                     maybe_not.empty__if_positive__not_option__if_negative +
                                                     [matcher_options.MATCHES_ARGUMENT]
                                                     ).followed_by(here_document_as_elements(['1.3']))
                self._check_with_source_variants(
                    argument_elements.as_arguments,
                    model_construction.model_of(actual_contents),
                    self.configuration.arrangement_for_contents(),
                    Expectation(main_result=maybe_not.pass__if_positive__fail__if_negative),
                )


class FullMatchTwoLinesWNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = lines_content(['123',
                                         '456'])
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            with self.subTest(maybe_with_transformer_option=transformer_option_arguments):
                argument_elements = ArgumentElements(transformer_option_arguments +
                                                     maybe_not.empty__if_positive__not_option__if_negative +
                                                     [matcher_options.MATCHES_ARGUMENT]
                                                     ).followed_by(here_document_as_elements(['1.3',
                                                                                              '4.*6']))
                self._check_with_source_variants(
                    argument_elements.as_arguments,
                    model_construction.model_of(actual_contents),
                    self.configuration.arrangement_for_contents(),
                    Expectation(main_result=maybe_not.pass__if_positive__fail__if_negative),
                )


class ActualContainsExtraLineAfterMatchingLines(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = lines_content(['123',
                                         '456',
                                         '789'])
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            with self.subTest(maybe_with_transformer_option=transformer_option_arguments):
                argument_elements = ArgumentElements(transformer_option_arguments +
                                                     maybe_not.empty__if_positive__not_option__if_negative +
                                                     [matcher_options.MATCHES_ARGUMENT]
                                                     ).followed_by(here_document_as_elements(['1.3',
                                                                                              '4.*6']))
                self._check_with_source_variants(
                    argument_elements.as_arguments,
                    model_construction.model_of(actual_contents),
                    self.configuration.arrangement_for_contents(),
                    Expectation(main_result=maybe_not.fail__if_positive__pass_if_negative),
                )
