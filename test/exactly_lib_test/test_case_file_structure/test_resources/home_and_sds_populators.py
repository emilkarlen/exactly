from typing import Sequence

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.files import file_structure


class HomeOrSdsPopulatorForRelOptionType(HomeOrSdsPopulator):
    def __init__(self,
                 relativity: RelOptionType,
                 dir_contents: file_structure.DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_home_or_sds(self, home_and_sds: HomeAndSds):
        root_path = REL_OPTIONS_MAP[self.relativity].root_resolver.from_home_and_sds(home_and_sds)
        self.dir_contents.write_to(root_path)


def in_tc_dir(relativity: RelOptionType,
              dir_contents: file_structure.DirContents) -> HomeOrSdsPopulator:
    return HomeOrSdsPopulatorForRelOptionType(relativity, dir_contents)


def empty() -> HomeOrSdsPopulator:
    return multiple([])


def multiple(populators: Sequence[HomeOrSdsPopulator]) -> HomeOrSdsPopulator:
    return _ListOfPopulators(populators)


class _ListOfPopulators(HomeOrSdsPopulator):
    def __init__(self, populator_list: Sequence[HomeOrSdsPopulator]):
        self.__populator_list = populator_list

    def populate_home_or_sds(self, home_and_sds: HomeAndSds):
        for populator in self.__populator_list:
            populator.populate_home_or_sds(home_and_sds)
