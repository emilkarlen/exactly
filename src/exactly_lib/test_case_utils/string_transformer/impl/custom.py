from abc import ABC

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.description_tree import renderers


class CustomStringTransformer(StringTransformer, ABC):
    """
    Base class for built in custom transformers.
    """

    def __init__(self, name: str):
        self._name = name
        self._structure = renderers.header_only(name)

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._structure

    def __str__(self):
        return str(type(self))
