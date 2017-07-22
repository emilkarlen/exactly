from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import NonHomePopulator
from exactly_lib_test.test_resources.file_structure import DirContents


def rel_option(relativity: RelNonHomeOptionType,
               dir_contents: DirContents) -> NonHomePopulator:
    return _NonHomePopulatorForRelativityOption(relativity,
                                                dir_contents)


def multiple(non_home_populator_list: list) -> NonHomePopulator:
    return _ListOfPopulators(non_home_populator_list)


def empty() -> NonHomePopulator:
    return _ListOfPopulators([])


class _NonHomePopulatorForRelativityOption(NonHomePopulator):
    def __init__(self,
                 relativity: RelNonHomeOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_non_home(self, sds: SandboxDirectoryStructure):
        root_path = relative_path_options.REL_NON_HOME_OPTIONS_MAP[self.relativity].root_resolver.from_non_home(sds)
        self.dir_contents.write_to(root_path)


class _ListOfPopulators(NonHomePopulator):
    def __init__(self, non_home_populator_list: list):
        self.__populator_list = non_home_populator_list

    def populate_non_home(self, sds: SandboxDirectoryStructure):
        for populator in self.__populator_list:
            populator.populate_non_home(sds)
