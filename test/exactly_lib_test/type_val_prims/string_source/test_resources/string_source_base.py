from abc import ABC
from typing import Optional

from exactly_lib.impls.types.string_source.source_from_contents import StringSourceStructureBuilderGetter
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder


def new_structure_builder() -> StringSourceStructureBuilder:
    return StringSourceStructureBuilder.of_details('test resource impl', ())


def new_structure_builder_with_header(header: str) -> StringSourceStructureBuilderGetter:
    def ret_val() -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder.of_details(header, ())

    return ret_val


class StringSourceTestImplBase(StringSource, ABC):
    def __init__(self, new_structure_builder_: Optional[StringSourceStructureBuilderGetter] = None):
        self._new_structure_builder = (
            new_structure_builder_with_header(str(type(self)))
            if new_structure_builder_ is None
            else
            new_structure_builder_
        )

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._new_structure_builder()
