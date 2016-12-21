import os
import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check, pfh_check
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulatorForSdsContents
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents, \
    SdsPopulator, SdsPopulatorForFileWithContentsThatDependOnSds, cwd_contents
from exactly_lib_test.test_resources.execution.utils import HomeAndSdsAction
from exactly_lib_test.test_resources.file_structure import DirContents, File

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'test-cwd'


class _CwdPopulator(SdsPopulator):
    def __init__(self, contents: DirContents):
        self.contents = contents

    def apply(self, sds: SandboxDirectoryStructure):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(sds)
        self.contents.write_to(sub_dir)


class RelativityOptionConfiguration:
    def __init__(self, cli_option: str):
        self._cli_option = cli_option

    @property
    def option_string(self) -> str:
        return self._cli_option

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    def populator_for_relativity_option_root_for_contents_from_fun(self,
                                                                   file_name: str,
                                                                   home_and_sds_2_file_contents_str
                                                                   ) -> HomeOrSdsPopulator:
        return _HomeOrSdsPopulatorForContentsThatDependOnHomeAndSds(file_name,
                                                                    home_and_sds_2_file_contents_str,
                                                                    self.populator_for_relativity_option_root)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        raise NotImplementedError()


class TestWithConfigurationAndRelativityOptionBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration):
        super().__init__(instruction_configuration)
        self.rel_opt = option_configuration

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(type(self.rel_opt))
                )


class TestWithConfigurationAndRelativityOptionAndNegationBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration,
                 is_negated: bool):
        super().__init__(instruction_configuration)
        self.rel_opt = option_configuration
        self.not_opt = NotOperatorInfo(is_negated)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(type(self.rel_opt)) + ' /\n' +
                'is_negated=' + str(self.not_opt.is_negated)
                )


def suite_for__conf__rel_opts__negations(instruction_configuration: InstructionTestConfiguration,
                                         relativity_options: list,
                                         test_cases: list) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        not_negated = [tc(instruction_configuration, option_configuration, False)
                       for tc in test_cases]
        negated = [tc(instruction_configuration, option_configuration, True)
                   for tc in test_cases]
        return unittest.TestSuite(not_negated + negated)

    return unittest.TestSuite([suite_for_option(relativity_option)
                               for relativity_option in relativity_options
                               ])


class RelativityOptionConfigurationForRelHome(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__(relative_path_options.REL_HOME_OPTION)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(validation_pre_sds=svh_check.is_validation_error())


class RelativityOptionConfigurationForRelSdsBase(RelativityOptionConfiguration):
    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        raise NotImplementedError()

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForSdsContents(self.populator_for_relativity_option_root__sds(contents))

    def populator_for_relativity_option_root_for_contents_from_sds_fun(self,
                                                                       file_name: str,
                                                                       sds_2_file_contents_str
                                                                       ) -> SdsPopulator:
        return SdsPopulatorForFileWithContentsThatDependOnSds(file_name,
                                                              sds_2_file_contents_str,
                                                              self.populator_for_relativity_option_root__sds)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())


class RelativityOptionConfigurationForRelCwd(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_CWD_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path().cwd()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return cwd_contents(contents)


class RelativityOptionConfigurationForRelCwdForTestCwdDir(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_CWD_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return _test_cwd_dir(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return _CwdPopulator(contents)


class RelativityOptionConfigurationForRelAct(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_ACT_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.act_dir

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return act_dir_contents(contents)


class RelativityOptionConfigurationForRelTmp(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_TMP_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.tmp.user_dir

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return tmp_user_dir_contents(contents)


def _get_cwd_path_and_make_dir_if_not_exists(sds: SandboxDirectoryStructure):
    ret_val = _test_cwd_dir(sds)
    if not ret_val.exists():
        os.mkdir(str(ret_val))
    return ret_val


class MkSubDirOfActAndMakeItCurrentDirectory(HomeAndSdsAction):
    def apply(self, home_and_sds: HomeAndSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(home_and_sds.sds)
        os.chdir(str(sub_dir))


def _test_cwd_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.act_dir / _SUB_DIR_OF_ACT_DIR_THAT_IS_CWD


class _HomeOrSdsPopulatorForContentsThatDependOnHomeAndSds(HomeOrSdsPopulator):
    def __init__(self,
                 file_name: str,
                 home_and_sds_2_file_contents_str,
                 dir_contents__2_home_or_sds_populator):
        """
        :type home_and_sds_2_file_contents_str: `HomeAndAds` -> str
        :type dir_contents__2_home_or_sds_populator: `DirContents` -> `HomeOrSdsPopulator`
        """
        self.file_name = file_name
        self.home_and_sds_2_file_contents_str = home_and_sds_2_file_contents_str
        self.dir_contents__2_home_or_sds_populator = dir_contents__2_home_or_sds_populator

    def write_to(self, home_and_sds: HomeAndSds):
        file_contents = self.home_and_sds_2_file_contents_str(home_and_sds)
        dir_contents = DirContents([
            File(self.file_name, file_contents)
        ])
        home_or_sds_populator = self.dir_contents__2_home_or_sds_populator(dir_contents)
        home_or_sds_populator.write_to(home_and_sds)
