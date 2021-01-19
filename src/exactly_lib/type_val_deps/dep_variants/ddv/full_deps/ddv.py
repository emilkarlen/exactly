from abc import abstractmethod, ABC
from typing import Generic, TypeVar

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_prims.description.details_structured import WithDetailsDescription
from exactly_lib.type_val_prims.description.logic_description import LogicValueDescription, NodeDescription, \
    DetailsDescription
from exactly_lib.type_val_prims.description.tree_structured import WithNodeDescription, StructureRenderer
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer

PRIMITIVE = TypeVar('PRIMITIVE')


class FullDepsDdv(Generic[PRIMITIVE],
                  DirDependentValue[ApplicationEnvironmentDependentValue[PRIMITIVE]],
                  ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.ConstantDdvValidator.new_success()

    @abstractmethod
    def description(self) -> LogicValueDescription:
        pass

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        pass


class FullDepsWithNodeDescriptionDdv(Generic[PRIMITIVE],
                                     FullDepsDdv[PRIMITIVE],
                                     WithNodeDescription,
                                     ABC):
    """A :class:`LogicDdv` that can report its structure in terms of a node tree"""

    def description(self) -> NodeDescription:
        return _DescriptionOfTreeStructure(self)


class FullDepsWithDetailsDescriptionDdv(Generic[PRIMITIVE],
                                        FullDepsDdv[PRIMITIVE],
                                        WithDetailsDescription,
                                        ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()

    def description(self) -> DetailsDescription:
        return _DetailsDescriptionOfWithDetails(self)


class _DescriptionOfTreeStructure(NodeDescription):
    def __init__(self, tree_structured: WithNodeDescription):
        self._tree_structured = tree_structured

    def structure(self) -> StructureRenderer:
        return self._tree_structured.structure()


class _DetailsDescriptionOfWithDetails(DetailsDescription):
    def __init__(self, with_details_description: WithDetailsDescription):
        self._with_details_description = with_details_description

    def details(self) -> DetailsRenderer:
        return self._with_details_description.describer
