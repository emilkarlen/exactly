import pathlib
from pathlib import Path

from exactly_lib.type_system.logic.string_model import TmpFilePathGenerator
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand


class PathGeneratorOfDirInTmpFileSpace(TmpFilePathGenerator):
    def __init__(self, root_dir_to_create_on_demand: pathlib.Path):
        """
        :param root_dir_to_create_on_demand: May or may not exist as a file.
        If it exists, it must be an empty dir.
        No one else than this object may create files in it.
        """
        self._dir_space = TmpDirFileSpaceAsDirCreatedOnDemand(root_dir_to_create_on_demand)

    def new_path(self) -> Path:
        return self._dir_space.new_path()
