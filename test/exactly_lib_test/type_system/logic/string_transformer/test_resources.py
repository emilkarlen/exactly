from abc import ABC
from typing import Iterable

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib_test.util.render.test_resources import renderers as renderers_tr


class StringTransformerTestImplBase(StringTransformer, ABC):
    @property
    def name(self) -> str:
        return str(type(self))

    def structure(self) -> StructureRenderer:
        return renderers_tr.structure_renderer_for_arbitrary_object(self)


class DeleteEverythingTransformer(StringTransformerTestImplBase):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return []


class EveryLineEmptyStringTransformer(StringTransformerTestImplBase):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda x: '', lines)
