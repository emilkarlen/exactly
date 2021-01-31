from contextlib import contextmanager
from typing import Optional, ContextManager, Iterator, TextIO

from exactly_lib.impls.types.string_source.contents.contents_with_cached_path import \
    ContentsWithCachedPathFromWriteToBase
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class ContentsOfStr(ContentsWithCachedPathFromWriteToBase):
    def __init__(self,
                 contents: str,
                 file_name: Optional[str],
                 tmp_file_space: DirFileSpace,
                 ):
        super().__init__(file_name)
        self._contents = contents
        self._tmp_file_space = tmp_file_space

    @property
    def may_depend_on_external_resources(self) -> bool:
        return False

    @property
    def as_str(self) -> str:
        return self._contents

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._contents.splitlines(keepends=True))

    def write_to(self, output: TextIO):
        output.write(self._contents)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space
