import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        ParseShouldFailWhenThereAreSuperfluousArguments,
        ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument,
        ActualFileIsEmpty,
        ActualFileIsNonEmpty,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class ParseShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(
            args('{maybe_not} {empty} superfluous-argument',
                 maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(source)


class ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(
    TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(
            args('{maybe_not} {empty} <<MARKER',
                 maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option),
            ['single line',
             'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(source)


class ActualFileIsEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{maybe_not} {empty}',
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass__if_un_negated_else__fail),
        )


class ActualFileIsNonEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{maybe_not} {empty}',
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents(
                'contents that makes the file non-empty',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail__if_un_negated_else__pass),
        )
