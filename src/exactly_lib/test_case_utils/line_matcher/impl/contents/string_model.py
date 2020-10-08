from contextlib import contextmanager
from typing import ContextManager, Iterator

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringModel(StringModelFromLinesBase):
    def __init__(self,
                 contents: str,
                 tmp_file_space: DirFileSpace,
                 ):
        super().__init__()
        self._contents = contents
        self.__tmp_file_space = tmp_file_space

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space

    @property
    def as_str(self) -> str:
        return self._contents

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter([self._contents])
