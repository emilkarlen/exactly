from typing import Optional, Callable, Generic

from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.string_matcher.base_class import StringMatcherImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, MODEL, \
    MatcherWTraceAndNegation, MatcherAdv
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.description_tree import tree
from exactly_lib_test.test_case_utils.description_tree.test_resources import ConstantNodeRendererTestImpl


class StringMatcherConstant(StringMatcherImplBase):
    """
    Matcher with constant result.

    TODO Replace with StringMatcherConstantTestImpl
    """

    def __init__(self, result: Optional[ErrorMessageResolver]):
        super().__init__()
        self._result = result

    @property
    def name(self) -> str:
        return 'any string' if self._result else 'no string'

    @property
    def option_description(self) -> str:
        return 'any string' if self._result else 'no string'

    @property
    def result_constant(self) -> Optional[ErrorMessageResolver]:
        return self._result

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return self._result

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        return self._new_tb().build_result(self._result is None)


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

    @property
    def option_description(self) -> str:
        return self.__structure.header

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return (
            None
            if self._result
            else
            err_msg_resolvers.constant('Unconditional False')
        )

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
        return advs.ConstantAdv(
            self._matcher(tcds)
        )
