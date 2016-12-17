import unittest

from exactly_lib.execution import environment_variables
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, \
    TestWithConfigurationAndNegationArgumentBase, suite_for__conf__not_argument, args
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ActResultProducer, \
    Expectation


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        _TestParseWithMissingRegExArgument,
        _TestParseWithSuperfluousArgument,

        _TestParseWithInvalidRegEx,
        _TestShouldFailWhenNoLineMatchesRegEx,
        _TestShouldPassWhenALineMatchesRegEx,
        _TestShouldPassWhenAWholeLineMatchesRegEx,

        _TestShouldReplaceEnvVarsWhenOptionIsGiven,
        _TestShouldNotReplaceEnvVarsWhenOptionIsNotGiven,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class ActResultProducerFromHomeAndSds2Str(ActResultProducer):
    def __init__(self, home_and_sds_2_str):
        self.home_and_sds_2_str = home_and_sds_2_str


class _TestParseWithMissingRegExArgument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{maybe_not} {contains}',
                                                   maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())))


class _TestParseWithSuperfluousArgument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{maybe_not} {contains} abc superfluous',
                                                   maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())))


class _TestParseWithInvalidRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{maybe_not} {contains} **',
                                                   maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())))


class _TestShouldFailWhenNoLineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        reg_ex = '123'
        self._check(
            self.configuration.source_for(args("{maybe_not} {contains} '{reg_ex}'",
                                               reg_ex=reg_ex,
                                               maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )


class _TestShouldPassWhenALineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = 'ATC'
        self._check(
            self.configuration.source_for(args("{maybe_not} {contains} '{reg_ex}'",
                                               reg_ex=reg_ex,
                                               maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class _TestShouldPassWhenAWholeLineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = '^MATCH$'
        self._check(
            self.configuration.source_for(args("{maybe_not} {contains} '{reg_ex}'",
                                               reg_ex=reg_ex,
                                               maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class _TestShouldReplaceEnvVarsWhenOptionIsGiven(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check(
            self.configuration.source_for(args("{replace_env_vars_option} {maybe_not} {contains} '{reg_ex}'",
                                               reg_ex=reg_ex,
                                               maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class _TestShouldNotReplaceEnvVarsWhenOptionIsNotGiven(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check(
            self.configuration.source_for(args("{maybe_not} {contains} '{reg_ex}'",
                                               reg_ex=reg_ex,
                                               maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )


_WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME.long)
