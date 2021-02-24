from typing import Generic, Callable

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.advs import ConstantMatcherAdv
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MODEL
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace


class MatcherDdvFromConstantPrimitive(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 primitive_value: MatcherWTrace[MODEL],
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(self._primitive_value)


class MatcherDdvFromPartsWConstantAdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 make_matcher: Callable[[TestCaseDs], MatcherWTrace[MODEL]],
                 structure: StructureRenderer,
                 ):
        self._make_matcher = make_matcher
        self._structure = structure

    def structure(self) -> StructureRenderer:
        return self._structure

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return ConstantMatcherAdv(self._make_matcher(tcds))
