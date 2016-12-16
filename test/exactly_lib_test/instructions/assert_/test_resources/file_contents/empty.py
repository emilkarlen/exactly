import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
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
    return unittest.TestSuite([tc(configuration, False) for tc in test_cases] +
                              [tc(configuration, True) for tc in test_cases])


class TestBase(TestWithConfigurationBase):
    def __init__(self,
                 configuration: InstructionTestConfiguration,
                 is_negated: bool):
        super().__init__(configuration)
        self.maybe_not = NotOperatorInfo(is_negated)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                'is_negated=' + str(self.maybe_not.is_negated)
                )


class ParseShouldFailWhenThereAreSuperfluousArguments(TestBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(
            args('{maybe_not} {empty} superfluous-argument',
                 maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option()))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(TestBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(
            args('{maybe_not} {empty} <<MARKER',
                 maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option()),
            ['single line',
             'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class ActualFileIsEmpty(TestBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {empty}',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class ActualFileIsNonEmpty(TestBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {empty}',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents(
                'contents that makes the file non-empty',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )
