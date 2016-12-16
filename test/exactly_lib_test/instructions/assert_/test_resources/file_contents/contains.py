import unittest

from exactly_lib.execution import environment_variables
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ActResultProducer, \
    Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check


class ActResultProducerFromHomeAndSds2Str(ActResultProducer):
    def __init__(self, home_and_sds_2_str):
        self.home_and_sds_2_str = home_and_sds_2_str


class _TestParseWithMissingRegExArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{contains}')))


class _TestParseWithSuperfluousArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{contains} abc superfluous')))


class _TestParseWithInvalidRegEx(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{contains} **')))


class _TestShouldFailWhenNoLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        reg_ex = '123'
        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class _TestShouldPassWhenALineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = 'ATC'
        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )


class _TestShouldPassWhenAWholeLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = '^MATCH$'
        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )


class _TestShouldReplaceEnvVarsWhenOptionIsGiven(TestWithConfigurationBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check(
            self.configuration.source_for(args("{replace_env_vars_option} {contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )


class _TestShouldNotReplaceEnvVarsWhenOptionIsNotGiven(TestWithConfigurationBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


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
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


def args(pattern: str, reg_ex: str = None) -> str:
    return pattern.format(contains=parsing.CONTAINS_ARGUMENT,
                          replace_env_vars_option=_WITH_REPLACED_ENV_VARS_OPTION,
                          reg_ex=reg_ex)


_WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME.long)
