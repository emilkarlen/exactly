from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, IO

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringModel(ABC):
    """Model for string transformers and string-matchers."""

    @property
    @abstractmethod
    def _tmp_file_space(self) -> DirFileSpace:
        pass

    @property
    @abstractmethod
    def as_file(self) -> Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.

        The path must not be modified on disk, neither its name nor its contents
        (unless the user is sure the file is not used in other contexts).

        The path may be read-only.

        :raises HardErrorException: Detected error
        """
        pass

    @property
    @abstractmethod
    def as_lines(self) -> ContextManager[Iterator[str]]:
        """
        Gives the lines of the file contents to check.

        Lines are generated each time this method is called,
        so if it is needed to iterate over them multiple times,
        it might be better to store the result in a file,
        using transformed_file_path.

        :raises HardErrorException: Detected error
        """
        pass

    def write_to(self, output: IO):
        """
        :raises HardErrorException: Detected error
        """
        with self.as_lines as lines:
            output.writelines(lines)
