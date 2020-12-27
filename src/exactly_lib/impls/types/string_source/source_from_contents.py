from typing import Callable

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder

StringSourceStructureBuilderGetter = Callable[[], StringSourceStructureBuilder]


class StringSourceWConstantContents(StringSource):
    """A :class:`StringSource` who's contents is not changed by freezing."""

    def __init__(self,
                 structure: StringSourceStructureBuilderGetter,
                 contents: StringSourceContents,
                 ):
        self._contents = contents
        self._structure = structure

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._structure()

    def freeze(self):
        pass

    def contents(self) -> StringSourceContents:
        return self._contents
