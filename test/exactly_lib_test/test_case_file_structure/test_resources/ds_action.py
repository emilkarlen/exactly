import os
import pathlib

from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolver


class PlainSdsAction:
    def apply(self, sds: SandboxDirectoryStructure):
        pass


class PlainTcdsAction:
    def apply(self, tcds: Tcds):
        pass


class PlainTcdsActionFromPlainSdsAction(PlainTcdsAction):
    def __init__(self, sds_action: PlainSdsAction):
        self._sds_action = sds_action

    def apply(self, tcds: Tcds):
        self._sds_action.apply(tcds.sds)


class MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs(PlainSdsAction):
    DIR_NAME = 'not-a-std-sub-dir-of-sds'

    def apply(self, sds: SandboxDirectoryStructure):
        dir_path = self.resolve_dir_path(sds)
        dir_path.mkdir(parents=True, exist_ok=True)
        os.chdir(str(dir_path))

    def resolve_dir_path(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.root_dir / self.DIR_NAME


MK_DIR_AND_CHANGE_TO_IT_INSIDE_OF_SDS_BUT_OUTSIDE_OF_ANY_OF_THE_RELATIVITY_OPTION_DIRS = (
    PlainTcdsActionFromPlainSdsAction(
        MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs()
    )
)


class MkSubDirAndMakeItCurrentDirectory(PlainTcdsAction):
    def __init__(self, sub_dir_resolver: SdsSubDirResolver):
        self.sub_dir_resolver = sub_dir_resolver

    def apply(self, tcds: Tcds):
        sub_dir = self.sub_dir_resolver.population_dir__create_if_not_exists(tcds.sds)
        os.chdir(str(sub_dir))
