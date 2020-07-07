from typing import Iterable

from exactly_lib.test_case_utils.string_transformer.impl.custom import CustomStringTransformer


class ToUpperCaseStringTransformer(CustomStringTransformer):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def is_identity_transformer(self) -> bool:
        return False

    def _transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class ToLowerCaseStringTransformer(CustomStringTransformer):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def is_identity_transformer(self) -> bool:
        return False

    def _transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.lower, lines)
