from pathlib import Path
from typing import Callable, Optional, ContextManager, Iterator, TextIO

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from .contents import frozen as _frozen
from .contents.contents_via_write_to import Writer


class StringSourceWithCachedFrozen(StringSource):
    def __init__(self,
                 new_structure_builder: Callable[[], StringSourceStructureBuilder],
                 unfrozen: StringSourceContents,
                 mem_buff_size: int,
                 name_suffix: Optional[str],
                 ):
        """
        :param unfrozen: Contents that probably not represents already
        frozen contents.
        """
        self._new_structure_builder = new_structure_builder
        self._mem_buff_size = mem_buff_size
        self._name_suffix = name_suffix

        self._contents = unfrozen
        self._is_frozen = False

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._new_structure_builder()

    def contents(self) -> StringSourceContents:
        return self._contents

    def freeze(self):
        if self._is_frozen:
            return

        self._contents = _FreezingStringSourceContents(
            self._contents,
            self._mem_buff_size,
            self._name_suffix,
        )

        self._is_frozen = True


class _FreezingStringSourceContents(StringSourceContents):
    def __init__(self,
                 unfrozen: StringSourceContents,
                 mem_buff_size: int,
                 file_name_suffix: Optional[str],
                 ):
        self._unfrozen = unfrozen
        self._contents = None
        self._mem_buff_size = mem_buff_size
        self._file_name_suffix = file_name_suffix

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._get_contents().may_depend_on_external_resources

    @property
    def as_str(self) -> str:
        return self._get_contents().as_str

    @property
    def as_file(self) -> Path:
        return self._get_contents().as_file

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._get_contents().as_lines

    def write_to(self, output: TextIO):
        self._get_contents().write_to(output)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._unfrozen.tmp_file_space

    def _get_contents(self) -> StringSourceContents:
        if self._contents is None:
            frozen = self._new_frozen()
            self._contents = frozen

        return self._contents

    def _new_frozen(self) -> StringSourceContents:
        return _frozen.frozen__from_write(
            self._mem_buff_size,
            _ContentsWriter(self._unfrozen),
            self._unfrozen.tmp_file_space,
            self._file_name_suffix,
        )


class _ContentsWriter(Writer):
    def __init__(self, contents: StringSourceContents):
        self._contents = contents

    def write(self, tmp_file_space: DirFileSpace, output: TextIO):
        self._contents.write_to(output)
