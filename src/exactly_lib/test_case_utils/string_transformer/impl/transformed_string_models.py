from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Callable, ContextManager

from exactly_lib.type_system.logic.impls import transformed_string_models
from exactly_lib.type_system.logic.impls.transformed_string_models import TransformedStringModelBase
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer


class StringTransformerFromLinesTransformer(StringTransformer, ABC):
    @abstractmethod
    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pass

    def transform(self, model: StringModel) -> StringModel:
        return transformed_string_models.TransformedStringModelFromLines(
            self._transform,
            model,
        )


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
