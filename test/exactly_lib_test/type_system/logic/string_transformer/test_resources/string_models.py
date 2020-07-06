from contextlib import contextmanager
from typing import Callable, Sequence, ContextManager, Iterator

from exactly_lib.type_system.logic.string_model import StringModel, TmpFilePathGenerator
from exactly_lib.type_system.logic.string_transformer import StringTransformerModel
from exactly_lib_test.type_system.logic.test_resources.string_models import StringModelFromLinesBase

StringTransFun = Callable[[StringTransformerModel], StringTransformerModel]


class ConstantTransformedStringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 value: Sequence[str],
                 transformed: StringModel,
                 ):
        super().__init__()
        self._value = value
        self._transformed = transformed

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._transformed._path_generator

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._value)


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
