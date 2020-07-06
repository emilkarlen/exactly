from abc import ABC

from exactly_lib.test_case_utils.string_models import transformed_model_from_lines
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer


class StringTransformerFromLinesTransformer(StringTransformer, ABC):
    def transform__new(self, model: StringModel) -> StringModel:
        return transformed_model_from_lines.TransformedStringModelFromLines(
            self.transform,
            model,
        )
