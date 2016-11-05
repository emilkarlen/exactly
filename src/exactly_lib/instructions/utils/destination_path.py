import enum
import pathlib

from exactly_lib.test_case.sandbox_directory_structure import ExecutionDirectoryStructure


class DestinationType(enum.Enum):
    REL_ACT_DIR = 0
    REL_TMP_DIR = 1
    REL_CWD = 2


class DestinationPath(tuple):
    def __new__(cls,
                destination_type: DestinationType,
                directory_argument: pathlib.PurePath):
        return tuple.__new__(cls, (destination_type, directory_argument))

    @property
    def destination_type(self) -> DestinationType:
        return self[0]

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self[1]

    def root_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        if self.destination_type is DestinationType.REL_ACT_DIR:
            return eds.act_dir
        elif self.destination_type is DestinationType.REL_TMP_DIR:
            return eds.tmp.user_dir
        else:
            return pathlib.Path.cwd()

    def resolved_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        return self.root_path(eds) / self.path_argument
