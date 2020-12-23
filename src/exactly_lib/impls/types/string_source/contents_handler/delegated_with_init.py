from pathlib import Path
from typing import IO, ContextManager, Iterator, Callable

from exactly_lib.impls.types.string_source.contents_handler.handler import ContentsHandler
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class DelegatedContentsHandlerWithInit(ContentsHandler):
    def __init__(self,
                 initializer: Callable[[], ContentsHandler],
                 may_depend_on_external_resources_of_uninitialized: Callable[[], bool],
                 get_tmp_file_space: Callable[[], DirFileSpace],
                 ):
        self._may_depend_on_external_resources_of_uninitialized = may_depend_on_external_resources_of_uninitialized
        self._initializer = initializer
        self._get_tmp_file_space = get_tmp_file_space
        self._delegated = None

    @property
    def may_depend_on_external_resources(self) -> bool:
        return (
            self._may_depend_on_external_resources_of_uninitialized()
            if self._delegated is None
            else
            self._delegated.may_depend_on_external_resources
        )

    @property
    def as_str(self) -> str:
        return self._get_delegated().as_str

    @property
    def as_file(self) -> Path:
        return self._get_delegated().as_file

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._get_delegated().as_lines

    def write_to(self, output: IO):
        self._get_delegated().write_to(output)

    def _get_delegated(self) -> ContentsHandler:
        if self._delegated is None:
            self._delegated = self._initializer()

        return self._delegated

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._get_tmp_file_space()
