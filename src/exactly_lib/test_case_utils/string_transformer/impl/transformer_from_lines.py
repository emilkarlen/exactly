from abc import ABC, abstractmethod
from typing import Iterator

from exactly_lib.test_case_utils.string_models import transformed_model_from_lines
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer


class StringTransformerFromLinesTransformer(StringTransformer, ABC):
    @abstractmethod
    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pass

    def transform(self, model: StringModel) -> StringModel:
        return transformed_model_from_lines.TransformedStringModelFromLines(
            self._transform,
            model,
        )
