from abc import ABC
from pathlib import Path

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.util.file_utils import misc_utils


class StringSourceContentsFromLinesBase(StringSourceContents, ABC):
    def __init__(self):
        self._as_file_path = None

    @property
    def as_file(self) -> Path:
        if self._as_file_path is None:
            self._as_file_path = self._to_file()
        return self._as_file_path

    def _to_file(self) -> Path:
        path = self.tmp_file_space.new_path()

        with misc_utils.open_and_make_read_only_on_close__text(path, 'x') as f:
            with self.as_lines as lines:
                f.writelines(lines)

        return path
