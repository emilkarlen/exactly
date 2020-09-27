from typing import Sequence

from exactly_lib.tcfs import relative_path_options
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib_test.tcfs.test_resources.dir_populator import NonHdsPopulator
from exactly_lib_test.test_resources.files.file_structure import DirContents


def rel_option(relativity: RelNonHdsOptionType,
               dir_contents: DirContents) -> NonHdsPopulator:
    return _NonHdsPopulatorForRelativityOption(relativity,
                                               dir_contents)


def multiple(non_hds_populator_list: Sequence[NonHdsPopulator]) -> NonHdsPopulator:
    return _ListOfPopulators(non_hds_populator_list)


def empty() -> NonHdsPopulator:
    return _ListOfPopulators([])


class _NonHdsPopulatorForRelativityOption(NonHdsPopulator):
    def __init__(self,
                 relativity: RelNonHdsOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_non_hds(self, sds: SandboxDs):
        root_path = relative_path_options.REL_NON_HDS_OPTIONS_MAP[self.relativity].root_resolver.from_non_hds(sds)
        self.dir_contents.write_to(root_path)


class _ListOfPopulators(NonHdsPopulator):
    def __init__(self, non_hds_populator_list: Sequence[NonHdsPopulator]):
        self.__populator_list = non_hds_populator_list

    def populate_non_hds(self, sds: SandboxDs):
        for populator in self.__populator_list:
            populator.populate_non_hds(sds)
