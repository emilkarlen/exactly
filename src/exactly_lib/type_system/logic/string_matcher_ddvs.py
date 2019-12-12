from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_matcher import StringMatcherDdv, StringMatcher


class StringMatcherConstantDdv(StringMatcherDdv):
    """
    A :class:`StringMatcherValue` that is a constant :class:`StringMatcher`
    """

    def __init__(self,
                 value: StringMatcher,
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator(),
                 ):
        self._value = value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringMatcher:
        return self._value
