from typing import Iterable

from exactly_lib.type_system.logic.string_transformer import StringTransformer


class ToUppercaseStringTransformer(StringTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class TransformedContentsSetup:
    def __init__(self,
                 original: str,
                 transformed: str):
        self.original = original
        self.transformed = transformed