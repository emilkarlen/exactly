from typing import Callable

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.tcfs.test_resources.tcds_populators import \
    TcdsPopulator
from exactly_lib_test.test_case_utils.string_matcher.test_resources.relativity_options import \
    RelativityOptionConfiguration
from exactly_lib_test.test_resources.files.file_structure import DirContents, File


def populator_for_relativity_option_root_for_contents_from_fun(conf: RelativityOptionConfiguration,
                                                               file_name: str,
                                                               tcds_2_file_contents_str
                                                               ) -> TcdsPopulator:
    return _HdsOrSdsPopulatorForContentsThatDependOnHdsAndSds(file_name,
                                                              tcds_2_file_contents_str,
                                                              conf.populator_for_relativity_option_root)


class _HdsOrSdsPopulatorForContentsThatDependOnHdsAndSds(TcdsPopulator):
    def __init__(self,
                 file_name: str,
                 tcds_2_file_contents_str: Callable[[TestCaseDs], str],
                 dir_contents__2_hds_or_sds_populator: Callable[[DirContents], TcdsPopulator]):
        self.file_name = file_name
        self.tcds_2_file_contents_str = tcds_2_file_contents_str
        self.dir_contents__2_hds_or_sds_populator = dir_contents__2_hds_or_sds_populator

    def populate_tcds(self, tcds: TestCaseDs):
        file_contents = self.tcds_2_file_contents_str(tcds)
        dir_contents = DirContents([
            File(self.file_name, file_contents)
        ])
        tcds_populator = self.dir_contents__2_hds_or_sds_populator(dir_contents)
        tcds_populator.populate_tcds(tcds)
