import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib_test.instructions.assert_.contents_of_file.test_resources.arguments_building import args
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.util.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.section_document.element_parsers.test_resources.exception_assertions import \
    assert_is_single_instruction_invalid_argument_exception
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    test_cases = [
        ParseShouldFailWhenActualIsFollowedByIllegalOptionOrString,
        ParseShouldFailWhenCheckIsMissing,
        ParseShouldFailWhenCheckIsIllegal,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class ParseShouldFailWhenActualIsFollowedByIllegalOptionOrString(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NameAndValue('illegal option',
                         option_syntax.long_option_syntax('this-is-an-illegal-option')),
            NameAndValue('illegal argument',
                         'this-is-an-illegal-argument'),
        ]
        parser = self.configuration.new_parser()
        for case in cases:
            with self.subTest(case_name=case.name):
                source = self.configuration.source_for(
                    args('{illegal_argument} {maybe_not} {empty}',
                         illegal_argument=case.value,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException) as cm:
                    parser.parse(source)
                assert_is_single_instruction_invalid_argument_exception().apply_with_message(
                    self,
                    cm.exception,
                    'exception from parser'
                )


class ParseShouldFailWhenCheckIsMissing(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not}',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException) as cm:
                    parser.parse(source)
                assert_is_single_instruction_invalid_argument_exception().apply_with_message(
                    self,
                    cm.exception,
                    'exception from parser'
                )


class ParseShouldFailWhenCheckIsIllegal(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        cases = [
            NameAndValue('unknown check',
                         'unknown_check'),
            NameAndValue('illegal option',
                         'this-is-an-illegal-argument'),
        ]
        parser = self.configuration.new_parser()
        for case in cases:
            for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
                with self.subTest(illegal_check=case.name,
                                  maybe_with_transformer_option=maybe_with_transformer_option):
                    source = self.configuration.source_for(
                        args('{maybe_with_transformer_option} {maybe_not} {illegal_check}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
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
