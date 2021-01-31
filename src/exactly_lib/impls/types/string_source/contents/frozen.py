import os
import pathlib
from contextlib import contextmanager
from typing import Optional, ContextManager, Iterator, TextIO

from exactly_lib.impls.types.string_source.contents import contents_of_existing_path, contents_of_str
from exactly_lib.impls.types.string_source.contents.contents_via_write_to import Writer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.util.file_utils import spooled_file
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


def frozen__from_write(mem_buff_size: int,
                       writer: Writer,
                       tmp_file_space: DirFileSpace,
                       file_name: Optional[str] = None,
                       ) -> StringSourceContents:
    def get_unused_path() -> pathlib.Path:
        return tmp_file_space.new_path(file_name)

    with spooled_file.SpooledTextFile(
            mem_buff_size,
            get_unused_path) as f:
        writer.write(tmp_file_space, f)

        if f.is_mem_buff:
            return contents_of_str.ContentsOfStr(f.mem_buff, file_name,
                                                 tmp_file_space)

        else:
            mb_contents = _contents_of_file__if_fits_within_mem_buff(f, mem_buff_size)

            return (
                contents_of_existing_path.StringSourceContentsOfExistingPath(f.path_of_file_on_disk,
                                                                             tmp_file_space)
                if mb_contents is None
                else
                _StringSourceContentsOfConstStrAndExistingPath(mb_contents, f.path_of_file_on_disk,
                                                               tmp_file_space)
            )


def _contents_of_file__if_fits_within_mem_buff(f: spooled_file.SpooledTextFile,
                                               mem_buff_size: int) -> Optional[str]:
    file_size = _size_of_file_on_disk(f)
    if file_size > mem_buff_size:
        return None
    else:
        f.seek(0, os.SEEK_SET)
        return f.read()


def _size_of_file_on_disk(f: spooled_file.SpooledTextFile) -> int:
    f.flush()
    return os.fstat(f.fileno()).st_size


class _StringSourceContentsOfConstStrAndExistingPath(StringSourceContents):
    def __init__(self,
                 contents_as_str: str,
                 contents_as_existing_file: pathlib.Path,
                 tmp_file_space: DirFileSpace,
                 ):
        self._contents_as_str = contents_as_str
        self._contents_as_lines = None
        self._contents_as_existing_file = contents_as_existing_file
        self._tmp_file_space = tmp_file_space

    @property
    def may_depend_on_external_resources(self) -> bool:
        return False

    @property
    def as_str(self) -> str:
        return self._contents_as_str

    @property
    def as_file(self) -> pathlib.Path:
        return self._contents_as_existing_file

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        if self._contents_as_lines is None:
            self._contents_as_lines = self._contents_as_str.splitlines(keepends=True)

        yield iter(self._contents_as_lines)

    def write_to(self, output: TextIO):
        output.write(self._contents_as_str)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space
