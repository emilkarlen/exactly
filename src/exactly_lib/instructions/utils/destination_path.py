import enum
import pathlib

from exactly_lib.instructions.utils.arg_parse.relative_path_options import RelOptionType, REL_OPTIONS_MAP
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


class DestinationType(enum.Enum):
    REL_ACT_DIR = 0
    REL_TMP_DIR = 1
    REL_CWD = 2


class DestinationPath(tuple):
    def __new__(cls,
                destination_type: RelOptionType,
                path_argument: pathlib.PurePath):
        return tuple.__new__(cls, (destination_type, path_argument))

    @property
    def destination_type(self) -> RelOptionType:
        return self[0]

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self[1]

    def root_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return REL_OPTIONS_MAP[self.destination_type].root_resolver.from_home_and_sds(home_and_sds)

    def resolved_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.root_path(home_and_sds) / self.path_argument

    def resolved_path_if_not_rel_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return REL_OPTIONS_MAP[self.destination_type].root_resolver.from_non_home(sds) / self.path_argument
