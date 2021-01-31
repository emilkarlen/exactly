from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, ContextManager, Optional, TextIO

from exactly_lib.impls.types.string_source.contents.contents_with_cached_path import \
    StringSourceContentsWithCachedPath
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class TransformedContentsViaAsLinesBase(StringSourceContentsWithCachedPath, ABC):
    def __init__(self,
                 source: StringSource,
                 file_name: Optional[str],
                 ):
        super().__init__()
        self._source = source
        self._file_name = file_name

    @property
    @abstractmethod
    def may_depend_on_external_resources(self) -> bool:
        pass

    @abstractmethod
    def _transform_lines(self, lines: Iterator[str]) -> Iterator[str]:
        pass

    @property
    def as_str(self) -> str:
        with self.as_lines as lines:
            return ''.join(lines)

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._source.contents().as_lines as lines:
            yield self._transform_lines(lines)

    def write_to(self, output: TextIO):
        with self.as_lines as lines:
            output.writelines(lines)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._source.contents().tmp_file_space

    def _to_file(self) -> Path:
        ret_val = self.tmp_file_space.new_path(self._file_name)
        with ret_val.open('w+') as f:
            self.write_to(f)

        return ret_val
