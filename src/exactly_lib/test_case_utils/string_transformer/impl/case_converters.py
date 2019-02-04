from typing import Iterable

from exactly_lib.type_system.logic.string_transformer import CustomStringTransformer


class ToUpperCaseStringTransformer(CustomStringTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class ToLowerCaseStringTransformer(CustomStringTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.lower, lines)
