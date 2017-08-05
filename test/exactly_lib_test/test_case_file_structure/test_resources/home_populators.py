from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator
from exactly_lib_test.test_resources.file_structure import DirContents


def empty() -> HomePopulator:
    return multiple([])


def multiple(home_populators: list) -> HomePopulator:
    return _ListOfPopulators(home_populators)


def case_home_dir_contents(contents: DirContents) -> HomePopulator:
    return contents_in(RelHomeOptionType.REL_HOME_CASE, contents)


def contents_in(relativity: RelHomeOptionType,
                dir_contents: DirContents) -> HomePopulator:
    return _HomePopulatorForRelHomeOptionType(relativity,
                                              dir_contents)


class _HomePopulatorForRelHomeOptionType(HomePopulator):
    def __init__(self, relativity: RelHomeOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_hds(self, hds: HomeDirectoryStructure):
        target_dir = relative_path_options.REL_HOME_OPTIONS_MAP[self.relativity].root_resolver.from_home(hds)
        self.dir_contents.write_to(target_dir)


class _ListOfPopulators(HomePopulator):
    def __init__(self, home_populators: list):
        for populator in home_populators:
            assert isinstance(populator, HomePopulator)
        self.__populator_list = home_populators

    def populate_hds(self, hds: HomeDirectoryStructure):
        for populator in self.__populator_list:
            assert isinstance(populator, HomePopulator)
            populator.populate_hds(hds)
