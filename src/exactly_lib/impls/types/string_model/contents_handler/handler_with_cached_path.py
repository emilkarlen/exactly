from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from exactly_lib.impls.types.string_model.contents_handler.handler import ContentsHandler
from exactly_lib.util.file_utils import misc_utils


class ContentsHandlerWithCachedPath(ContentsHandler, ABC):
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


class ContentsHandlerWithCachedPathFromWriteTo(ContentsHandlerWithCachedPath, ABC):
    """Caches the file path, when generated the first time.

    The file contents is generated via `write_to`.
    """

    def __init__(self, file_name: Optional[str] = None):
        super().__init__()
        self._file_name = file_name

    def _to_file(self) -> Path:
        path = self.tmp_file_space.new_path(self._file_name)

        with misc_utils.open_and_make_read_only_on_close__p(path, 'x') as f:
            self.write_to(f)

        return path
