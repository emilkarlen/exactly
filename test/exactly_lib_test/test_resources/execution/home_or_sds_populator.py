from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution.sds_check import sds_populator


class HomeOrSdsPopulator:
    def write_to(self, home_and_sds: HomeAndSds):
        raise NotImplementedError()


class HomeOrSdsPopulatorForHomeContents(HomeOrSdsPopulator):
    def __init__(self, home_dir_contents: file_structure.DirContents):
        self.home_dir_contents = home_dir_contents

    def write_to(self, home_and_sds: HomeAndSds):
        self.home_dir_contents.write_to(home_and_sds.home_dir_path)


class HomeOrSdsPopulatorForSdsContents(HomeOrSdsPopulator):
    def __init__(self, sds_contents: sds_populator.SdsPopulator):
        self.sds_contents = sds_contents

    def write_to(self, home_and_sds: HomeAndSds):
        self.sds_contents.apply(home_and_sds.sds)


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
