import os
import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EQUALS_ARGUMENT
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestWithParserBase, \
    TestConfigurationForStdout, TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    OutputContentsToStdout, WriteFileToHomeDir, ActResultContentsSetup, OutputContentsToStderr, WriteFileToCurrentDir
from exactly_lib_test.instructions.assert_.test_resources.file_contents.contains import TestWithConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestConfiguration, args
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult, ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.test_resources import home_and_sds_test
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulatorForHomeContents, \
    HomeOrSdsPopulator, HomeOrSdsPopulatorForSdsContents
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2, argument_list_source

SUB_DIR_OF_ACT_THAT_IS_CWD = 'test-cwd'


def _get_cwd_path_and_make_dir_if_not_exists(sds: SandboxDirectoryStructure):
    ret_val = sds.act_dir / SUB_DIR_OF_ACT_THAT_IS_CWD
    if not ret_val.exists():
        os.mkdir(str(ret_val))
    return ret_val


class MkSubDirOfActAndChangeToIt(home_and_sds_test.Action):
    def apply(self, home_and_sds: HomeAndSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(home_and_sds.sds)
        os.chdir(str(sub_dir))


class CwdPopulator(HomeOrSdsPopulator):
    def __init__(self, contents: DirContents):
        self.contents = contents

    def write_to(self, home_and_sds: HomeAndSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(home_and_sds.sds)
        self.contents.write_to(sub_dir)


class RelativityOptionConfiguration:
    def __init__(self, cli_option: str):
        self.cli_option = cli_option

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    def expect_file_for_expected_contents_is_invalid(self) -> Expectation:
        raise NotImplementedError()


class TestWithConfigurationAndRelativityOptionBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: TestConfiguration,
                 option_configuration: RelativityOptionConfiguration):
        super().__init__(instruction_configuration)
        self.option_configuration = option_configuration

    def shortDescription(self):
        return (str(type(self)) + ' / ' +
                str(type(self.configuration)) + ' / ' +
                str(type(self.option_configuration))
                )


class RelativityOptionConfigurationForRelHome(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__(relative_path_options.REL_HOME_OPTION)

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)

    def expect_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(validation_pre_sds=svh_check.is_validation_error())


class RelativityOptionConfigurationForRelSdsBase(RelativityOptionConfiguration):
    def expect_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())


class RelativityOptionConfigurationForRelCwd(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_CWD_OPTION)

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return CwdPopulator(contents)


class RelativityOptionConfigurationForRelAct(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_ACT_OPTION)

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForSdsContents(act_dir_contents(contents))


class RelativityOptionConfigurationForRelTmp(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_TMP_OPTION)

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForSdsContents(tmp_user_dir_contents(contents))


class _ValidationErrorWhenComparisonFileDoesNotExist(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} non-existing-file.txt',
                     relativity_option=self.option_configuration.cli_option)),
            ArrangementPostAct(post_sds_population_action=MkSubDirOfActAndChangeToIt()),
            self.option_configuration.expect_file_for_expected_contents_is_invalid(),
        )


class _ValidationErrorWhenComparisonFileIsADirectory(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} dir',
                     relativity_option=self.option_configuration.cli_option)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.contents_at_option_relativity_root(
                    DirContents([empty_dir('dir')])),
                post_sds_population_action=MkSubDirOfActAndChangeToIt()
            ),
            self.option_configuration.expect_file_for_expected_contents_is_invalid(),
        )


class _FaiWhenContentsDiffer(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} f.txt',
                     relativity_option=self.option_configuration.cli_option)),
            self.configuration.arrangement_for_actual_and_expected(
                'actual',
                self.option_configuration.contents_at_option_relativity_root(
                    DirContents([File('f.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndChangeToIt()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class _PassWhenContentsEquals(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} f.txt',
                     relativity_option=self.option_configuration.cli_option)),
            self.configuration.arrangement_for_actual_and_expected(
                'expected',
                self.option_configuration.contents_at_option_relativity_root(
                    DirContents([File('f.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndChangeToIt()),
            Expectation(main_result=pfh_check.is_pass()),
        )


class FileContentsHereDoc(TestWithParserBase):
    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        raise NotImplementedError()

    def pass__when__contents_equals(self):
        self._run(
            argument_list_source([EQUALS_ARGUMENT, '<<EOF'],
                                 ['single line',
                                  'EOF']),
            arrangement(act_result_producer=ActResultProducerFromActResult(
                self._act_result_with_contents(lines_content(['single line'])))),
            is_pass(),
        )


class FileContentsHereDocFORStdout(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stdout_contents=contents_on_tested_channel,
                         stderr_contents=contents_on_other_channel)


class FileContentsHereDocFORStderr(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stderr_contents=contents_on_tested_channel,
                         stdout_contents=contents_on_other_channel)


class ReplacedEnvVars(TestWithParserBase):
    SOURCE_FILE_NAME = 'with-replaced-env-vars.txt'

    def __init__(self,
                 act_result_contents_setup: ActResultContentsSetup,
                 method_name):
        super().__init__(method_name)
        self._act_result_contents_setup = act_result_contents_setup

    def pass__when__contents_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToHomeDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_home_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),

        )

    def fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToHomeDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_home_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToCurrentDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_cwd_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),
        )

    def fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToCurrentDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_cwd_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestReplacedEnvVarsFORStdout(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(OutputContentsToStdout(), method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()


class TestReplacedEnvVarsFORStderr(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(OutputContentsToStderr(), method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()


_RELATIVITY_OPTION_CONFIGURATIONS = [
    RelativityOptionConfigurationForRelHome(),
    RelativityOptionConfigurationForRelCwd(),
    RelativityOptionConfigurationForRelAct(),
    RelativityOptionConfigurationForRelTmp(),
]


def suite_for(instruction_configuration: TestConfiguration) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        test_cases = [
            _ValidationErrorWhenComparisonFileDoesNotExist,
            _ValidationErrorWhenComparisonFileIsADirectory,
            _FaiWhenContentsDiffer,
            _PassWhenContentsEquals,
        ]
        return unittest.TestSuite([tc(instruction_configuration, option_configuration)
                                   for tc in test_cases])

    return unittest.TestSuite([suite_for_option(relativity_option_configuration)
                               for relativity_option_configuration in _RELATIVITY_OPTION_CONFIGURATIONS])


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(FileContentsHereDocFORStdout),
        unittest.makeSuite(FileContentsHereDocFORStderr),

        unittest.makeSuite(TestReplacedEnvVarsFORStdout),
        unittest.makeSuite(TestReplacedEnvVarsFORStderr),

        suite_for(TestConfigurationForStdout()),
        suite_for(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
