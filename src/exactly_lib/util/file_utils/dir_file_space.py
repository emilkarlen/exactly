import pathlib
from abc import ABC, abstractmethod
from typing import Optional


class DirFileSpace(ABC):
    """
    A directory serving as a space for a sequence of automatically named files.
    """

    @abstractmethod
    def new_path(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        """
        :param name_suffix: Dir separator characters are replaces with a non-dir-sep character.
        :returns: A path, with name_suffix as suffix of the file name.
        """
        pass

    @abstractmethod
    def new_path_as_existing_dir(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        """
        :param name_suffix: Dir separator characters are replaces with a non-dir-sep character.
        :returns: A path that is an existing empty dir, with name_suffix as suffix of the file name.
        """
        pass

    @abstractmethod
    def sub_dir_space(self, name_suffix: Optional[str] = None) -> 'DirFileSpace':
        """
        :param name_suffix: Dir separator characters are replaces with a non-dir-sep character.
        :return: A file space in a new empty directory, with name_suffix as suffix of the file name.
        """
        pass
