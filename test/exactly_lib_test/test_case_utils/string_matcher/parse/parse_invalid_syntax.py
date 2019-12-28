import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher as sut
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib_test.section_document.element_parsers.test_resources.exception_assertions import \
    assert_is_single_instruction_invalid_argument_exception
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import test_configuration
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ParseShouldFailWhenActualIsFollowedByIllegalOptionOrString(),
        ParseShouldFailWhenCheckIsMissing(),
        ParseShouldFailWhenCheckIsIllegal(),
    ])


class ParseShouldFailWhenActualIsFollowedByIllegalOptionOrString(test_configuration.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #
        cases = [
            NameAndValue('illegal option',
                         option_syntax.long_option_syntax('this-is-an-illegal-option')),
            NameAndValue('illegal argument',
                         'this-is-an-illegal-argument'),
        ]
        parser = sut.string_matcher_parser()
        for case in cases:
            with self.subTest(case_name=case.name):
                source = test_configuration.source_for(
                    args('{illegal_argument} {maybe_not} {empty}',
                         illegal_argument=case.value,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException) as cm:
                    parser.parse(source)
                assert_is_single_instruction_invalid_argument_exception().apply_with_message(
                    self,
                    cm.exception,
                    'exception from parser'
                )


class ParseShouldFailWhenCheckIsMissing(test_configuration.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        parser = sut.string_matcher_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = test_configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not}',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException) as cm:
                    parser.parse(source)
                assert_is_single_instruction_invalid_argument_exception().apply_with_message(
                    self,
                    cm.exception,
                    'exception from parser'
                )


class ParseShouldFailWhenCheckIsIllegal(test_configuration.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        cases = [
            NameAndValue('illegal option',
                         'this-is-an-illegal-argument'),
        ]
        parser = sut.string_matcher_parser()
        for case in cases:
            for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
                with self.subTest(illegal_check=case.name,
                                  maybe_with_transformer_option=maybe_with_transformer_option):
                    source = test_configuration.source_for(
                        args('{maybe_with_transformer_option} {maybe_not} {illegal_check}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                             illegal_check=case.value,
                             ),
                    )
                    with self.assertRaises(SingleInstructionInvalidArgumentException) as cm:
                        parser.parse(source)
                    assert_is_single_instruction_invalid_argument_exception().apply_with_message(
                        self,
                        cm.exception,
                        'exception from parser'
                    )
