from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, IO

from exactly_lib.impls.types.string_source.contents_handler.handler import ContentsHandler
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringSourceViaContentsHandler(StringSource, ABC):
    """Base class for :class:`StringSource`s who's contents
    is given by a :class:`ContentsHandler`."""

    @abstractmethod
    def _get_contents(self) -> ContentsHandler:
        pass

    @property
    def as_str(self) -> str:
        return self._get_contents().as_str

    @property
    def as_file(self) -> Path:
        return self._get_contents().as_file

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._get_contents().as_lines

    def write_to(self, output: IO):
        return self._get_contents().write_to(output)

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self._get_contents().tmp_file_space
