import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, args, InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        ParseOfEmptyShouldFailWhenThereAreSuperfluousArguments,
        ParseOfEmptyShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument,
        ParseOfNotEmptyShouldFailWhenThereAreSuperfluousArguments,
        ParseOfNotEmptyShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument,
        EmptyShouldPassWhenActualFileIsEmpty,
        EmptyShouldFailWhenActualFileIsNonEmpty,
        NotEmptyShouldFailWhenActualFileIsEmpty,
        NotEmptyShouldPassWhenActualFileIsNonEmpty,
    ]
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


class ParseOfEmptyShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(args('{empty} superfluous-argument'))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class ParseOfEmptyShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(TestWithConfigurationBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(args('{empty} <<MARKER'),
                                               ['single line',
                                                'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class ParseOfNotEmptyShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(args('{not} {empty} superfluous-argument'))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class ParseOfNotEmptyShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(TestWithConfigurationBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        source = self.configuration.source_for(args('{not} {empty} <<MARKER'),
                                               ['single line',
                                                'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class EmptyShouldPassWhenActualFileIsEmpty(TestWithConfigurationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(args('{empty}')),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )


class EmptyShouldFailWhenActualFileIsNonEmpty(TestWithConfigurationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(args('{empty}')),
            self.configuration.arrangement_for_contents(
                'contents that makes the file non-empty',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class NotEmptyShouldFailWhenActualFileIsEmpty(TestWithConfigurationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(args('{not} {empty}')),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class NotEmptyShouldPassWhenActualFileIsNonEmpty(TestWithConfigurationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(args('{not} {empty}')),
            self.configuration.arrangement_for_contents(
                'contents that makes the file non-empty',
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )
