from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, IO

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringModel(ABC):
    """Access to a string in various forms.

    The string is backed by a constant "string source".
    The string is constant, unless the "string source" may give different result
    at different times - e.g. an external program.

    The public methods are just different kind of access to the same string.

    Maybe a "freeze" method should be added to store the string in a file (if needed),
    to guarantee that the string is constant, even over time.
    """

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
        The string as a sequence of lines.

        New-line characters are included.

        :raises HardErrorException: Detected error
        """
        pass

    def write_to(self, output: IO):
        """
        Writes the string to a file.

        :raises HardErrorException: Detected error
        """
        with self.as_lines as lines:
            output.writelines(lines)
