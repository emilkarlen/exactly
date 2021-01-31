from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, TextIO

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace

BUFFER_SIZE = 2 ** 16


class StringSourceContentsOfExistingPath(StringSourceContents):
    def __init__(self,
                 existing_regular_file_path: Path,
                 tmp_file_space: DirFileSpace,
                 ):
        self._existing_regular_file_path = existing_regular_file_path
        self._tmp_file_space = tmp_file_space

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

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

    def write_to(self, output: TextIO):
        with self.as_lines as lines:
            output.writelines(lines)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space
