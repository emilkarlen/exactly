import unittest

from exactly_lib.impls.types.string_matcher import matcher_options, parse_string_matcher as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    ParseExpectation, ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements, \
    here_document_as_elements
from exactly_lib_test.impls.types.string_matcher.test_resources import test_configuration
from exactly_lib_test.impls.types.string_matcher.test_resources import test_configuration as tc
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building import args, \
    FULL_MATCH_ARGUMENT
from exactly_lib_test.impls.types.string_matcher.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES, TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS
from exactly_lib_test.impls.types.string_models.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.impls.types.test_resources.validation import pre_sds_validation_fails__w_any_msg
from exactly_lib_test.section_document.test_resources import parse_source_assertions  as asrt_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ParseShouldFailWhenRegexArgumentIsMissing(),
        ValidationShouldFailPreWhenHardCodedRegexIsInvalid(),
        StringTransformerShouldBeValidated(),

        FullMatchSingleLineWoNewline(),
        PartialMatchSingleLineWoNewline(),
        FullMatchDoNotAcceptPartialMatchSingleLineWoNewline(),

        FullMatchSingleLineWNewline(),
        FullMatchTwoLinesWNewline(),

        PartialMatchAcceptsExtraLinesBeforeOrAfterMatchingLines(),
        FullMatchDoNotAcceptExtraLineAfterMatchingLines(),
    ])


class StringTransformerShouldBeValidated(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for case in failing_validation_cases():
            with self.subTest(validation_case=case.name):
                self._check(
                    test_configuration.source_for(
                        args('{transformer_option} {maybe_not} {matches} .',
                             transformer_option=case.value.transformer_arguments_string,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_constructor.empty(self),
                    Arrangement(
                        symbols=case.value.symbol_context.symbol_table
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.value.symbol_context.references_assertion
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class ValidationShouldFailPreWhenHardCodedRegexIsInvalid(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            for maybe_full_match in FULL_MATCH_OPTION_ALTERNATIVES:
                with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option,
                                  maybe_full_match=maybe_full_match):
                    self._check_with_source_variants(
                        test_configuration.arguments_for(
                            args('{maybe_with_transformer_option} {maybe_not} {matches} {maybe_full_match} **',
                                 maybe_with_transformer_option=maybe_with_transformer_option,
                                 maybe_full_match=maybe_full_match,
                                 maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                        model_constructor.empty(self),
                        Arrangement(),
                        Expectation(
                            execution=ExecutionExpectation(
                                validation=pre_sds_validation_fails__w_any_msg()
                            ),
                        )
                    )


class ParseShouldFailWhenRegexArgumentIsMissing(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = sut.parsers().full
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            for maybe_full_match in FULL_MATCH_OPTION_ALTERNATIVES:
                with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option,
                                  maybe_full_match=maybe_full_match):
                    source = test_configuration.source_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matches} {maybe_full_match}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_full_match=maybe_full_match,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                    )
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)


class FullMatchSingleLineWoNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = '123'
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            for maybe_full_match in FULL_MATCH_OPTION_ALTERNATIVES:
                with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option,
                                  maybe_full_match=maybe_full_match):
                    self._check_with_source_variants(
                        test_configuration.arguments_for(
                            args('{maybe_with_transformer_option} {maybe_not} {matches} {maybe_full_match} 1.3',
                                 maybe_with_transformer_option=maybe_with_transformer_option,
                                 maybe_full_match=maybe_full_match,
                                 maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                        model_constructor.of_str(self, actual_contents),
                        arrangement_w_tcds(),
                        Expectation(
                            execution=ExecutionExpectation(
                                main_result=maybe_not.pass__if_positive__fail__if_negative
                            ),
                        ),
                    )


class PartialMatchSingleLineWoNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = '01234'
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    test_configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matches} 1.3',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_constructor.of_str(self, actual_contents),
                    arrangement_w_tcds(),
                    Expectation(
                        execution=ExecutionExpectation(
                            main_result=maybe_not.pass__if_positive__fail__if_negative
                        ),
                    ),
                )


class FullMatchDoNotAcceptPartialMatchSingleLineWoNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = '01234'
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    test_configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matches} {full_match} 1.3',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
                    model_constructor.of_str(self, actual_contents),
                    arrangement_w_tcds(),
                    Expectation(
                        execution=ExecutionExpectation(
                            main_result=maybe_not.fail__if_positive__pass_if_negative
                        ),
                    ),
                )


class FullMatchSingleLineWNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = lines_content(['123'])
        here_doc = here_document_as_elements(['1.3'])
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            with self.subTest(maybe_with_transformer_option=transformer_option_arguments):
                argument_elements = ArgumentElements(transformer_option_arguments +
                                                     maybe_not.empty__if_positive__not_option__if_negative +
                                                     [matcher_options.MATCHES_ARGUMENT]
                                                     ).followed_by(here_doc)
                self._check(
                    argument_elements.as_remaining_source,
                    model_constructor.of_str(self, actual_contents),
                    arrangement_w_tcds(),
                    Expectation(
                        ParseExpectation(
                            source=asrt_source.is_at_end_of_line(1 + len(here_doc.following_lines)),
                        ),
                        ExecutionExpectation(
                            main_result=maybe_not.pass__if_positive__fail__if_negative
                        ),
                    ),
                )


class FullMatchTwoLinesWNewline(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        actual_contents = lines_content(['123',
                                         '456'])
        here_doc = here_document_as_elements(['1.3', '4.*6'])
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            for maybe_full_match in FULL_MATCH_OPTION_ALTERNATIVES_ELEMENTS:
                with self.subTest(maybe_with_transformer_option=transformer_option_arguments,
                                  maybe_full_match=maybe_full_match):
                    argument_elements = ArgumentElements(transformer_option_arguments +
                                                         maybe_not.empty__if_positive__not_option__if_negative +
                                                         [matcher_options.MATCHES_ARGUMENT] +
                                                         maybe_full_match
                                                         ).followed_by(here_doc)
                    self._check(
                        argument_elements.as_remaining_source,
                        model_constructor.of_str(self, actual_contents),
                        arrangement_w_tcds(),
                        Expectation(
                            ParseExpectation(
                                source=asrt_source.is_at_end_of_line(1 + len(here_doc.following_lines)),
                            ),
                            ExecutionExpectation(
                                main_result=maybe_not.pass__if_positive__fail__if_negative
                            ),
                        ),
                    )


class PartialMatchAcceptsExtraLinesBeforeOrAfterMatchingLines(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        regex_lines = ['1.3',
                       '4.*6']
        here_doc = here_document_as_elements(regex_lines)

        actual_contents_cases = [
            lines_content(['123',
                           '456',
                           '789']
                          ),
            lines_content(['000,'
                           '123',
                           '456']
                          ),
        ]
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            for actual_contents in actual_contents_cases:
                with self.subTest(maybe_with_transformer_option=transformer_option_arguments,
                                  actual_contents=actual_contents):
                    argument_elements = ArgumentElements(transformer_option_arguments +
                                                         maybe_not.empty__if_positive__not_option__if_negative +
                                                         [matcher_options.MATCHES_ARGUMENT]
                                                         ).followed_by(here_doc)
                    self._check(
                        argument_elements.as_remaining_source,
                        model_constructor.of_str(self, actual_contents),
                        arrangement_w_tcds(),
                        Expectation(
                            ParseExpectation(
                                source=asrt_source.is_at_end_of_line(1 + len(here_doc.following_lines)),
                            ),
                            ExecutionExpectation(
                                main_result=maybe_not.pass__if_positive__fail__if_negative
                            ),
                        ),
                    )


class FullMatchDoNotAcceptExtraLineAfterMatchingLines(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        regex_lines = ['1.3',
                       '4.*6']
        here_doc_of_reg_ex = here_document_as_elements(regex_lines)
        actual_contents = lines_content(['123',
                                         '456',
                                         '789'])
        for transformer_option_arguments in TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS:
            with self.subTest(maybe_with_transformer_option=transformer_option_arguments):
                argument_elements = ArgumentElements(transformer_option_arguments +
                                                     maybe_not.empty__if_positive__not_option__if_negative +
                                                     [matcher_options.MATCHES_ARGUMENT,
                                                      FULL_MATCH_ARGUMENT]
                                                     ).followed_by(here_doc_of_reg_ex)
                self._check(
                    argument_elements.as_remaining_source,
                    model_constructor.of_str(self, actual_contents),
                    arrangement_w_tcds(),
                    Expectation(
                        ParseExpectation(
                            source=asrt_source.is_at_end_of_line(1 + len(here_doc_of_reg_ex.following_lines))
                        ),
                        ExecutionExpectation(
                            main_result=maybe_not.fail__if_positive__pass_if_negative
                        ),
                    ),
                )


FULL_MATCH_OPTION_ALTERNATIVES = [
    '',
    FULL_MATCH_ARGUMENT,
]

FULL_MATCH_OPTION_ALTERNATIVES_ELEMENTS = [
    [],
    [FULL_MATCH_ARGUMENT],
]
