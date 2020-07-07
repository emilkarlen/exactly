from contextlib import contextmanager
from typing import ContextManager, Iterator, Sequence

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import TmpFilePathGenerator


class ConstantRootStringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 value: Sequence[str],
                 tmp_file_path_generator: TmpFilePathGenerator,
                 ):
        super().__init__()
        self._value = value
        self._tmp_file_path_generator = tmp_file_path_generator

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._tmp_file_path_generator

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._value)
