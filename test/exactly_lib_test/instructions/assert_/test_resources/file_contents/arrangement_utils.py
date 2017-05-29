from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_resources.file_structure import DirContents, File


def populator_for_relativity_option_root_for_contents_from_fun(conf: RelativityOptionConfiguration,
                                                               file_name: str,
                                                               home_and_sds_2_file_contents_str
                                                               ) -> HomeOrSdsPopulator:
    return _HomeOrSdsPopulatorForContentsThatDependOnHomeAndSds(file_name,
                                                                home_and_sds_2_file_contents_str,
                                                                conf.populator_for_relativity_option_root)


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
