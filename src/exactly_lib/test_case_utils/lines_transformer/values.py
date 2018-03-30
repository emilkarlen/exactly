from typing import Sequence

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.lines_transformer import transformers
from exactly_lib.type_system.logic.lines_transformer import LinesTransformerValue, LinesTransformer


class LinesTransformerConstantValue(LinesTransformerValue):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: LinesTransformer):
        self._value = value

    def value_when_no_dir_dependencies(self) -> LinesTransformer:
        return self._value

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LinesTransformer:
        return self._value


class LinesTransformerSequenceValue(LinesTransformerValue):
    def __init__(self, sequence: Sequence[LinesTransformerValue]):
        self._sequence = sequence

    def value_when_no_dir_dependencies(self) -> LinesTransformer:
        return transformers.SequenceLinesTransformer([
            transformer.value_when_no_dir_dependencies()
            for transformer in self._sequence
        ])

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> transformers.SequenceLinesTransformer:
        return transformers.SequenceLinesTransformer([
            transformer.value_of_any_dependency(home_and_sds)
            for transformer in self.transformers
        ])
