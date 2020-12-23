from pathlib import Path
from typing import Callable, Optional, IO, ContextManager, Iterator

from exactly_lib.impls.types.string_source.contents_handler.handler import ContentsHandler
from exactly_lib.impls.types.string_source.contents_handler.string_source import StringSourceViaContentsHandler
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from .contents_handler import frozen as _frozen
from .contents_handler.handler_via_write_to import Writer


class StringSourceWithCachedFrozen(StringSourceViaContentsHandler):
    def __init__(self,
                 new_structure_builder: Callable[[], StringSourceStructureBuilder],
                 unfrozen: ContentsHandler,
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

        self._contents_handler = unfrozen
        self._is_frozen = False

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._new_structure_builder()

    def freeze(self):
        if self._is_frozen:
            return

        self._set_contents(
            _FreezingContentsHandler(
                self._contents_handler,
                self._mem_buff_size,
                self._name_suffix,
                self._set_contents,
            )
        )

        self._is_frozen = True

    def _get_contents(self) -> ContentsHandler:
        return self._contents_handler

    def _set_contents(self, new_handler: ContentsHandler):
        self._contents_handler = new_handler


class _FreezingContentsHandler(ContentsHandler):
    def __init__(self,
                 unfrozen: ContentsHandler,
                 mem_buff_size: int,
                 file_name_suffix: Optional[str],
                 set_frozen_handler: Callable[[ContentsHandler], None],
                 ):
        self._unfrozen = unfrozen
        self._mem_buff_size = mem_buff_size
        self._file_name_suffix = file_name_suffix
        self._set_frozen_handler = set_frozen_handler

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._set_and_get_frozen().may_depend_on_external_resources

    @property
    def as_str(self) -> str:
        return self._set_and_get_frozen().as_str

    @property
    def as_file(self) -> Path:
        return self._set_and_get_frozen().as_file

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._set_and_get_frozen().as_lines

    def write_to(self, output: IO):
        self._set_and_get_frozen().write_to(output)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._unfrozen.tmp_file_space

    def _set_and_get_frozen(self) -> ContentsHandler:
        frozen = self._frozen()
        self._set_frozen_handler(frozen)
        return frozen

    def _frozen(self) -> ContentsHandler:
        return _frozen.frozen__from_write(
            self._mem_buff_size,
            _ContentsHandlerWriter(self._unfrozen),
            self._unfrozen.tmp_file_space,
            self._file_name_suffix,
        )


class _ContentsHandlerWriter(Writer):
    def __init__(self, contents: ContentsHandler):
        self._contents = contents

    def write(self, tmp_file_space: DirFileSpace, output: IO):
        self._contents.write_to(output)
