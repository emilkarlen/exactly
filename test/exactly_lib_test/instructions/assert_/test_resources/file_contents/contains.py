import unittest

import exactly_lib.instructions.assert_.utils.file_contents.instruction_options
from exactly_lib.execution import environment_variables
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
        _ParseWithMissingRegExArgument,
        _ParseWithSuperfluousArgument,

        _ParseWithInvalidRegEx,
        _NoLineMatchesRegEx,
        _ALineMatchesRegEx,
        _AWholeLineMatchesRegEx,

        _ShouldReplaceEnvVarsWhenOptionIsGiven,
        _ShouldNotReplaceEnvVarsWhenOptionIsNotGiven,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class ActResultProducerFromHomeAndSds2Str(ActResultProducer):
    def __init__(self, home_and_sds_2_str):
        self.home_and_sds_2_str = home_and_sds_2_str


class _ParseWithMissingRegExArgument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().parse(
                self.configuration.source_for(
                    args('{maybe_not} {contains}',
                         maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)))


class _ParseWithSuperfluousArgument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().parse(
                self.configuration.source_for(
                    args('{maybe_not} {contains} abc superfluous',
                         maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)))


class _ParseWithInvalidRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().parse(
                self.configuration.source_for(
                    args('{maybe_not} {contains} **',
                         maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)))


class _NoLineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        reg_ex = '123'
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {contains} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail__if_un_negated_else__pass),
        )


class _ALineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = 'ATC'
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {contains} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass__if_un_negated_else__fail),
        )


class _AWholeLineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = '^MATCH$'
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {contains} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass__if_un_negated_else__fail),
        )


class _ShouldReplaceEnvVarsWhenOptionIsGiven(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{replace_env_vars_option} {maybe_not} {contains} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass__if_un_negated_else__fail),
        )


class _ShouldNotReplaceEnvVarsWhenOptionIsNotGiven(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {contains} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option)),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail__if_un_negated_else__pass),
        )


_WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(
    exactly_lib.instructions.assert_.utils.file_contents.instruction_options.WITH_REPLACED_ENV_VARS_OPTION_NAME.long)
