from typing import Iterable

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    StringTransformerTestImplBase


class ToUppercaseStringTransformer(StringTransformerTestImplBase):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def structure(self) -> StructureRenderer:
        return renderers.header_only(str(type(self)))

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class TransformedContentsSetup:
    def __init__(self,
                 original: str,
                 transformed: str):
        self.original = original
        self.transformed = transformed
