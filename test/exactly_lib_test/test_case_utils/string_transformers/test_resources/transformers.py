from typing import Iterable

from exactly_lib.type_system.logic.string_transformer import CustomStringTransformer


class CustomStringTransformerTestImpl(CustomStringTransformer):
    def __init__(self):
        super().__init__(str(type(self)))

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should not be used')
