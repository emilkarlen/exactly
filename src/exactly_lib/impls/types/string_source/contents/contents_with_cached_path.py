from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, TextIO

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.util.file_utils import misc_utils


class StringSourceContentsWithCachedPath(StringSourceContents, ABC):
    """Caches the file path, when generated the first time."""

    def __init__(self):
        self._as_file_path = None

    @property
    def as_file(self) -> Path:
        if self._as_file_path is None:
            self._as_file_path = self._to_file()
        return self._as_file_path

    @abstractmethod
    def _to_file(self) -> Path:
        pass


class ContentsWithCachedPathFromWriteToBase(StringSourceContentsWithCachedPath, ABC):
    """Caches the file path, when generated the first time.

    The file contents is generated via `write_to`.
    """

    def __init__(self, file_name: Optional[str] = None):
        super().__init__()
        self._file_name = file_name

    def _to_file(self) -> Path:
        path = self.tmp_file_space.new_path(self._file_name)

        with misc_utils.open_and_make_read_only_on_close__text(path, 'x') as f:
            self.write_to(f)

        return path


class ContentsWithCachedPathFromAsLinesBase(ContentsWithCachedPathFromWriteToBase, ABC):
    """Caches the file path, when generated the first time.

    The contents is generated via `as_lines`.
    """

    def __init__(self, file_name: Optional[str] = None):
        super().__init__(file_name)

    @property
    def as_str(self) -> str:
        with self.as_lines as lines:
            return ''.join(lines)

    def write_to(self, output: TextIO):
        with self.as_lines as lines:
            output.writelines(lines)
