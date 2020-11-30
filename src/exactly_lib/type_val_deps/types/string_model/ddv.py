from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithNodeDescriptionDdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.type_val_prims.string_model.structure_builder import StringModelStructureBuilder

StringModelAdv = ApplicationEnvironmentDependentValue[StringModel]


class StringModelDdv(FullDepsWithNodeDescriptionDdv[StringModel], ABC):
    @abstractmethod
    def new_structure_builder(self) -> StringModelStructureBuilder:
        """"Gives a new object, for each invokation"""
        pass

    def structure(self) -> StructureRenderer:
        return self.new_structure_builder().build()
