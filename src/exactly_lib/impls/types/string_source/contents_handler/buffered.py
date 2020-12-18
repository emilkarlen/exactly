import pathlib
import tempfile
from contextlib import contextmanager
from typing import Optional, ContextManager, Iterator, IO, Union

from exactly_lib.impls.types.string_source.contents_handler.handler import ContentsHandler
from exactly_lib.impls.types.string_source.contents_handler.handler_of_existing_path import \
    ContentsHandlerOfExistingPath
from exactly_lib.impls.types.string_source.contents_handler.handler_via_write_to import Writer
from exactly_lib.impls.types.string_source.contents_handler.handler_with_cached_path import \
    ContentsHandlerWithCachedPathFromWriteTo
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


def write_to_mem_or_file(tmp_file_space: DirFileSpace,
                         mem_buff_size: int,
                         writer: Writer,
                         file_name: Optional[str] = None,
                         ) -> Union[str, pathlib.Path]:
    raise NotImplementedError('todo')


def handler_from_write(tmp_file_space: DirFileSpace,
                       mem_buff_size: int,
                       writer: Writer,
                       file_name: Optional[str] = None,
                       ) -> ContentsHandler:
    path = tmp_file_space.new_path(file_name)
    with tempfile.SpooledTemporaryFile(
            mode='w+',
            max_size=mem_buff_size,
            dir=str(path.parent),
            prefix=path.name) as f:
        writer.write(tmp_file_space, f)
        if f._rolled:
            return ContentsHandlerOfExistingPath(pathlib.Path(f.name),
                                                 tmp_file_space)
        else:
            f.seek(0)
            return ContentsHandlerFromMemory(f.read(),
                                             file_name,
                                             tmp_file_space)


class ContentsHandlerFromMemory(ContentsHandlerWithCachedPathFromWriteTo):
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

    def write_to(self, output: IO):
        output.write(self._contents)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space
