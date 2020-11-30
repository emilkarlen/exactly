from abc import ABC

from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.type_val_prims.string_model.structure_builder import StringModelStructureBuilder


class StringModelTestImplBase(StringModel, ABC):
    def new_structure_builder(self) -> StringModelStructureBuilder:
        return StringModelStructureBuilder.of_details(str(type(self)), ())
