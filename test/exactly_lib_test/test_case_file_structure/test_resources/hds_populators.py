from typing import Sequence

from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HdsPopulator
from exactly_lib_test.test_resources.files.file_structure import DirContents


def empty() -> HdsPopulator:
    return multiple([])


def multiple(home_populators: Sequence[HdsPopulator]) -> HdsPopulator:
    return _ListOfPopulators(home_populators)


def hds_case_dir_contents(contents: DirContents) -> HdsPopulator:
    return contents_in(RelHdsOptionType.REL_HDS_CASE, contents)


def contents_in(relativity: RelHdsOptionType,
                dir_contents: DirContents) -> HdsPopulator:
    return _HdsPopulatorForRelHdsOptionType(relativity,
                                            dir_contents)


class _HdsPopulatorForRelHdsOptionType(HdsPopulator):
    def __init__(self,
                 relativity: RelHdsOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_hds(self, hds: HomeDirectoryStructure):
        target_dir = relative_path_options.REL_HDS_OPTIONS_MAP[self.relativity].root_resolver.from_hds(hds)
        self.dir_contents.write_to(target_dir)


class _ListOfPopulators(HdsPopulator):
    def __init__(self, home_populators: Sequence[HdsPopulator]):
        for populator in home_populators:
            assert isinstance(populator, HdsPopulator)
        self.__populator_list = home_populators

    def populate_hds(self, hds: HomeDirectoryStructure):
        for populator in self.__populator_list:
            assert isinstance(populator, HdsPopulator)
            populator.populate_hds(hds)
