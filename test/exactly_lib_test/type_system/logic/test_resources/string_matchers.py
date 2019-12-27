from typing import Callable, Generic

from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_matcher.base_class import StringMatcherImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, MODEL, \
    MatcherWTraceAndNegation, MatcherAdv
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.description_tree import tree
from exactly_lib_test.test_case_utils.description_tree.test_resources import ConstantNodeRendererTestImpl


class StringMatcherConstantTestImpl(StringMatcherImplBase):
    """Matcher with constant result."""

    def __init__(self,
                 result: bool,
                 structure: tree.Node[None] = tree.Node('test impl constant', None, (), ()),
                 ):
        super().__init__()
        self._result = result
        self.__structure = structure

    @property
    def name(self) -> str:
        return self.__structure.header

    def _structure(self) -> StructureRenderer:
        return ConstantNodeRendererTestImpl(self.__structure)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        return self._new_tb().build_result(self._result)


class MatcherDdvFromPartsTestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 structure: StructureRenderer,
                 matcher: Callable[[Tcds], MatcherWTraceAndNegation[MODEL]],
                 validator: DdvValidator = ddv_validation.constant_success_validator()):
        self._structure = structure
        self._validator = validator
        self._matcher = matcher

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            self._matcher(tcds)
        )
