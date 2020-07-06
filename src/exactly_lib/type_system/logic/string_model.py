from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator


class TmpFilePathGenerator(ABC):
    """Generates any number of unused paths."""

    @abstractmethod
    def new_path(self) -> Path:
        """
        :return: A path that is safe to create. A new path is given on each invokation.
        """
        pass


class StringModel(ABC):
    """Model for string transformers and string-matchers."""

    @property
    @abstractmethod
    def _path_generator(self) -> TmpFilePathGenerator:
        pass

    @property
    @abstractmethod
    def as_file(self) -> Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.
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
        """
        pass
