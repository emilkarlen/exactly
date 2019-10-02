from abc import ABC
from typing import Iterable

from exactly_lib.type_system.logic.string_transformer import StringTransformer


class StringTransformerTestImplBase(StringTransformer, ABC):
    @property
    def name(self) -> str:
        return str(type(self))


class DeleteEverythingTransformer(StringTransformerTestImplBase):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return []


class EveryLineEmptyStringTransformer(StringTransformerTestImplBase):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda x: '', lines)
