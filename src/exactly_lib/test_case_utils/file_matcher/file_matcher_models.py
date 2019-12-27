from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel


class FileMatcherModelForDescribedPath(FileMatcherModel):
    def __init__(self, path: DescribedPath):
        self._path = path

    @property
    def path(self) -> DescribedPath:
        """Path of the file to match. May or may not exist."""
        return self._path
