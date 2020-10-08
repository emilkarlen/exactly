from abc import ABC
from contextlib import contextmanager
from typing import Callable, ContextManager, Iterator

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace

StringTransFun = Callable[[Iterator[str]], Iterator[str]]


class TransformedStringModelBase(StringModel, ABC):
    def __init__(self,
                 transformed: StringModel,
                 ):
        super().__init__()
        self._transformed = transformed

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self._transformed._tmp_file_space


class TransformedStringModelFromLines(StringModelFromLinesBase, TransformedStringModelBase):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringModel,
                 transformation_may_depend_on_external_resources: bool,
                 ):
        StringModelFromLinesBase.__init__(self)
        TransformedStringModelBase.__init__(self, transformed)
        self._transformation = transformation
        self._transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources

    @property
    def may_depend_on_external_resources(self) -> bool:
        return (self._transformation_may_depend_on_external_resources or
                self._transformed.may_depend_on_external_resources)

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._transformed.as_lines as lines:
            yield self._transformation(lines)
