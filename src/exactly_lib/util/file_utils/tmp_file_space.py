import pathlib
from abc import ABC, abstractmethod


class TmpFileSpace(ABC):
    @abstractmethod
    def new_path(self) -> pathlib.Path:
        pass

    def new_path_as_existing_dir(self) -> pathlib.Path:
        path = self.new_path()
        path.mkdir(parents=True, exist_ok=False)
        return path


class TmpDirFileSpace(ABC):
    """
    A directory serving as a space for temporary files.
    """

    @abstractmethod
    def new_path(self) -> pathlib.Path:
        pass

    @abstractmethod
    def new_path_as_existing_dir(self) -> pathlib.Path:
        pass

    @abstractmethod
    def sub_dir_space(self) -> 'TmpDirFileSpace':
        pass
