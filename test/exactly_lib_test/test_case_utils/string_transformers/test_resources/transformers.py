from typing import Iterable

from exactly_lib.test_case_utils.string_transformer.impl.custom import CustomStringTransformer


class CustomStringTransformerTestImpl(CustomStringTransformer):
    def __init__(self):
        super().__init__(str(type(self)))

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should not be used')
