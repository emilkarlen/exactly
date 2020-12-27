from abc import ABC

from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder


class StringSourceTestImplBase(StringSource, ABC):
    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder.of_details(str(type(self)), ())


def new_structure_builder() -> StringSourceStructureBuilder:
    return StringSourceStructureBuilder.of_details('test resource impl', ())
