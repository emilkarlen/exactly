from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, ContextManager, Iterator

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace

StringTransFun = Callable[[Iterator[str]], Iterator[str]]


class TransformedStringModelBase(StringModel, ABC):
    def __init__(self,
                 transformed: StringModel,
                 ):
        super().__init__()
        self._transformed = transformed

    @property
    def _tmp_file_space(self) -> TmpDirFileSpace:
        return self._transformed._tmp_file_space


class TransformedStringModelFromLines(StringModelFromLinesBase, TransformedStringModelBase):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringModel,
                 ):
        StringModelFromLinesBase.__init__(self)
        TransformedStringModelBase.__init__(self, transformed)
        self._transformation = transformation

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._transformed.as_lines as lines:
            yield self._transformation(lines)


class TransformedStringModelFromFileCreatedOnDemand(TransformedStringModelBase):
    def __init__(self,
                 mk_file: Callable[[StringModel], Path],
                 transformed: StringModel,
                 ):
        super().__init__(transformed)
        self._mk_file = mk_file
        self._file_created_on_demand = None

    @property
    def as_file(self) -> Path:
        if self._file_created_on_demand is None:
            self._file_created_on_demand = self._mk_file(self._transformed)

        return self._file_created_on_demand

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines
