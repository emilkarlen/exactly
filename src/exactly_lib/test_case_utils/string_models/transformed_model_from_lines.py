from contextlib import contextmanager
from typing import Callable, ContextManager, Iterator

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import StringModel, TmpFilePathGenerator

StringTransFun = Callable[[Iterator[str]], Iterator[str]]


class TransformedStringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringModel,
                 ):
        super().__init__()
        self._transformation = transformation
        self._transformed = transformed

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._transformed._path_generator

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._transformed.as_lines as lines:
            yield self._transformation(lines)
