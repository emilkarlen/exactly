import unittest

from exactly_lib.execution import environment_variables
from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ActResultProducer, \
    Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActEnvironment, \
    ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class TestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        raise NotImplementedError()

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class TestConfigurationForStdFile(TestConfiguration):
    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        return new_source2(argument_tail)

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        act_result = self.act_result(actual_contents)
        act_result_producer = ActResultProducerFromActResult(act_result)
        return instruction_check.ArrangementPostAct(act_result_producer=act_result_producer)

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        raise NotImplementedError()


class _ActResultProducerFromHomeAndSds2Str(ActResultProducer):
    def __init__(self, home_and_sds_2_str):
        self.home_and_sds_2_str = home_and_sds_2_str


class _ActResultProducerForStdout(_ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stdout_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class _ActResultProducerForStderr(_ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stderr_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class TestConfigurationForStdout(TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(act_result_producer=_ActResultProducerForStdout(home_and_sds_2_str))

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stdout_contents=contents_of_tested_file)


class TestConfigurationForStderr(TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(act_result_producer=_ActResultProducerForStderr(home_and_sds_2_str))

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stderr_contents=contents_of_tested_file)


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: TestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: SingleInstructionParserSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)


class TestParseMatchesWithMissingRegExArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{contains}')))


class TestParseMatchesWithSuperfluousArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for(args('{contains} abc superfluous')))


class TestParseMatchesWithInvalidRegEx(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(
                self.configuration.source_for('{contains} **'))


class TestMatchesShouldFailWhenNoLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        reg_ex = '123'
        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents(actual_contents),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestMatchesShouldPassWhenALineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = 'ATC'
        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents(actual_contents),
            Expectation(main_result=pfh_check.is_pass()),
        )


class TestMatchesShouldPassWhenAWholeLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = '^MATCH$'
        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents(actual_contents),
            Expectation(main_result=pfh_check.is_pass()),
        )


class TestMatchesShouldReplaceEnvVarsWhenOptionIsGiven(TestWithConfigurationBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check(
            self.configuration.source_for(args("{replace_env_vars_option} {contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents_from_fun(home_dir_path_name),
            Expectation(main_result=pfh_check.is_pass()),
        )


class TestMatchesShouldNotReplaceEnvVarsWhenOptionIsNotGiven(TestWithConfigurationBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        reg_ex = environment_variables.ENV_VAR_HOME

        self._check(
            self.configuration.source_for(args("{contains} '{reg_ex}'", reg_ex)),
            self.configuration.arrangement_for_contents_from_fun(home_dir_path_name),
            Expectation(main_result=pfh_check.is_fail()),
        )


def suite_for_matches(configuration: TestConfiguration) -> unittest.TestSuite:
    test_cases = [
        TestParseMatchesWithMissingRegExArgument,
        TestParseMatchesWithSuperfluousArgument,

        TestParseMatchesWithInvalidRegEx,
        TestMatchesShouldFailWhenNoLineMatchesRegEx,
        TestMatchesShouldPassWhenALineMatchesRegEx,
        TestMatchesShouldPassWhenAWholeLineMatchesRegEx,

        TestMatchesShouldReplaceEnvVarsWhenOptionIsGiven,
        TestMatchesShouldNotReplaceEnvVarsWhenOptionIsNotGiven,
    ]
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_matches(TestConfigurationForStdout()),
        suite_for_matches(TestConfigurationForStderr()),
    ])


def args(pattern: str, reg_ex: str = None) -> str:
    return pattern.format(contains=parsing.CONTAINS_ARGUMENT,
                          replace_env_vars_option=_WITH_REPLACED_ENV_VARS_OPTION,
                          reg_ex=reg_ex)


_WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME.long)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
