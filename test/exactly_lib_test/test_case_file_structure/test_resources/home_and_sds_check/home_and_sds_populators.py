from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents


class HomeOrSdsPopulator:
    def write_to(self, home_and_sds: HomeAndSds):
        raise NotImplementedError()


class HomeOrSdsPopulatorForHomeContents(HomeOrSdsPopulator):
    def __init__(self, home_dir_contents: file_structure.DirContents):
        self.home_dir_contents = home_dir_contents

    def write_to(self, home_and_sds: HomeAndSds):
        self.home_dir_contents.write_to(home_and_sds.home_dir_path)


class HomeOrSdsPopulatorForRelOptionType(HomeOrSdsPopulator):
    def __init__(self,
                 relativity: RelOptionType,
                 dir_contents: file_structure.DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def write_to(self, home_and_sds: HomeAndSds):
        root_path = REL_OPTIONS_MAP[self.relativity].root_resolver.from_home_and_sds(home_and_sds)
        self.dir_contents.write_to(root_path)


class HomeOrSdsPopulatorForSdsContents(HomeOrSdsPopulator):
    def __init__(self, sds_contents: sds_populator.SdsPopulator):
        self.sds_contents = sds_contents

    def write_to(self, home_and_sds: HomeAndSds):
        self.sds_contents.populate_sds(home_and_sds.sds)


def empty() -> HomeOrSdsPopulator:
    return multiple([])


def multiple(populators: list) -> HomeOrSdsPopulator:
    return _ListOfPopulators(populators)


class _ListOfPopulators(HomeOrSdsPopulator):
    def __init__(self, populator_list: list):
        self.__populator_list = populator_list

    def write_to(self, home_and_sds: HomeAndSds):
        for populator in self.__populator_list:
            populator.write_to(home_and_sds)


class HomeAndSdsContents(tuple):
    def __new__(cls,
                home_dir_contents: DirContents = empty_dir_contents(),
                sds_contents: sds_populator.SdsPopulator = sds_populator.empty()):
        return tuple.__new__(cls, (home_dir_contents,
                                   sds_contents))

    @property
    def home_dir_contents(self) -> DirContents:
        return self[0]

    @property
    def sds_contents(self) -> sds_populator.SdsPopulator:
        return self[1]
