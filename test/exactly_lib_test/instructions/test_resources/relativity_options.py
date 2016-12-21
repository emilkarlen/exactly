import pathlib

from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check, pfh_check
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulatorForSdsContents
from exactly_lib_test.test_resources.execution.sds_check.sds_populator import act_dir_contents, tmp_user_dir_contents, \
    SdsPopulator, SdsPopulatorForFileWithContentsThatDependOnSds, cwd_contents
from exactly_lib_test.test_resources.file_structure import DirContents, File


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


class RelativityOptionConfigurationForRelHome(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__(relative_path_options.REL_HOME_OPTION)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(validation_pre_sds=svh_check.is_validation_error())


class RelativityOptionConfigurationForRelSds(RelativityOptionConfiguration):
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


class RelativityOptionConfigurationForRelCwd(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(relative_path_options.REL_CWD_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path().cwd()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return cwd_contents(contents)


class RelativityOptionConfigurationForRelAct(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(relative_path_options.REL_ACT_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.act_dir

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return act_dir_contents(contents)


class RelativityOptionConfigurationForRelTmp(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(relative_path_options.REL_TMP_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.tmp.user_dir

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return tmp_user_dir_contents(contents)


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
