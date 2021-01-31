from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, TextIO

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringSourceContents(ABC):
    """Access to the variants of the contents of a :class:`StringSource`"""

    @property
    @abstractmethod
    def may_depend_on_external_resources(self) -> bool:
        """
        Tells if the model probably depends on (heavy) resources such as
         - files
         - program execution

        If this method gives False - it should be relatively cheap to
        access it using func:`as_str`, for example.

        The return value is allowed to vary over time - the source may become
        independent on external resources via caching, e.g.

        The name is intentionally vague, so that an implementation
        can give True, even if it cannot guarantee that there are
        such dependencies.
        The idea is that an implementation should give False iff
        it can guarantee that there are no (heavy) external resources.

        :raises HardErrorException: Detected error
        """
        pass

    @property
    def as_str(self) -> str:
        """
        See also :func:`may_depend_on_external_resources`

        :raises HardErrorException: Detected error
        """
        with self.as_lines as lines:
            return ''.join(lines)

    @property
    @abstractmethod
    def as_file(self) -> Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.

        May indirectly freeze the contents (see `:func:StringSource:freeze`).
        (Is this indirect freeze good? Maybe a new file should be generated each time if
        depends on external resources, to avoid such freezing.)

        The file is located in a temporary directory.

        The path must not be modified on disk, neither its name nor its contents
        (unless the user can guarantee the file is not used in other contexts).

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

        This method generates the contents lazily (via the returned iterator),
        and thus is the preferred access to the contents if the full contents
        may not be needed.

        :raises HardErrorException: Detected error
        """
        pass

    def write_to(self, output: TextIO):
        """
        Writes the string to a file.

        :raises HardErrorException: Detected error
        """
        with self.as_lines as lines:
            output.writelines(lines)

    @property
    @abstractmethod
    def tmp_file_space(self) -> DirFileSpace:
        pass
