from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, IO

from exactly_lib.impls.types.string_model.contents_handler.handler import ContentsHandler
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace

BUFFER_SIZE = 2 ** 16


class ContentsHandlerOfExistingPath(ContentsHandler):
    def __init__(self,
                 existing_regular_file_path: Path,
                 tmp_file_space: DirFileSpace,
                 ):
        self._existing_regular_file_path = existing_regular_file_path
        self._tmp_file_space = tmp_file_space

    @property
    def as_file(self) -> Path:
        return self._existing_regular_file_path

    @property
    def as_str(self) -> str:
        with self._existing_regular_file_path.open() as f:
            return f.read()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._existing_regular_file_path.open() as lines:
            yield lines

    def write_to(self, output: IO):
        # TODO Would like to have other kind of buffering than line buffering -
        # the natural buffer size for the file.
        # But have not found out how to read buffer chunks.
        with self.as_lines as lines:
            output.writelines(lines)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space
