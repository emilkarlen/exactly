from abc import ABC
from typing import List

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir, FileSystemElement


class DirArgumentHelper(ABC):
    def __init__(self,
                 checked_dir_location: RelOptionType = RelOptionType.REL_TMP,
                 checked_dir_name: str = 'checked-dir',
                 ):
        self.location = checked_dir_location
        self.name = checked_dir_name

    @property
    def path_sdv(self) -> PathSdv:
        return path_sdvs.of_rel_option_with_const_file_name(self.location,
                                                            self.name)

    def tcds_populator_for_dir_with_contents(self,
                                             contents: List[FileSystemElement],
                                             ) -> TcdsPopulator:
        return tcds_populators.TcdsPopulatorForRelOptionType(
            self.location,
            DirContents([
                Dir(self.name, contents)
            ])
        )

    def tcds_arrangement_dir_with_contents(self,
                                           checked_dir_contents: List[FileSystemElement],
                                           ) -> TcdsArrangement:
        return TcdsArrangement(
            tcds_contents=self.tcds_populator_for_dir_with_contents(
                checked_dir_contents
            ),
        )
