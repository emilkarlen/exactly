from typing import Generic

from exactly_lib.symbol.logic.matcher import T
from exactly_lib.test_case.validation import pre_or_post_value_validation
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation


class MatcherDdvFromConstantPrimitive(Generic[T], MatcherDdv[T]):
    def __init__(self,
                 primitive_value: MatcherWTraceAndNegation[T],
                 validator: PreOrPostSdsValueValidator =
                 pre_or_post_value_validation.constant_success_validator(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherDdv[T]:
        return self._primitive_value
