from typing import Sequence

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.tcfs.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.test_resources.files import file_structure


class TcdsPopulatorForRelOptionType(TcdsPopulator):
    def __init__(self,
                 relativity: RelOptionType,
                 dir_contents: file_structure.DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_tcds(self, tcds: TestCaseDs):
        root_path = REL_OPTIONS_MAP[self.relativity].root_resolver.from_tcds(tcds)
        self.dir_contents.write_to(root_path)


def in_tc_dir(relativity: RelOptionType,
              dir_contents: file_structure.DirContents) -> TcdsPopulator:
    return TcdsPopulatorForRelOptionType(relativity, dir_contents)


def empty() -> TcdsPopulator:
    return multiple([])


def multiple(populators: Sequence[TcdsPopulator]) -> TcdsPopulator:
    return _ListOfPopulators(populators)


class _ListOfPopulators(TcdsPopulator):
    def __init__(self, populator_list: Sequence[TcdsPopulator]):
        self.__populator_list = populator_list

    def populate_tcds(self, tcds: TestCaseDs):
        for populator in self.__populator_list:
            populator.populate_tcds(tcds)
