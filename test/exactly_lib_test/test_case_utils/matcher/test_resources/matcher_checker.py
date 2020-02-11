from typing import TypeVar, Generic, Callable, Type

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult, MatcherDdv
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicTypeSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker

MODEL = TypeVar('MODEL')

ModelConstructor = Callable[[FullResolvingEnvironment], MODEL]


class MatcherPropertiesConfiguration(
    Generic[MODEL],
    CommonPropertiesConfiguration[MatcherWTraceAndNegation[MODEL],
                                  Callable[[FullResolvingEnvironment], MODEL],
                                  MatchingResult]):
    def __init__(self,
                 expected_logic_value_type: LogicValueType,
                 expected_object_type: Type[LogicTypeSdv],
                 ):
        self._sdv_checker = LogicTypeSdvPropertiesChecker(expected_logic_value_type,
                                                          expected_object_type)

    def apply(self,
              primitive: MatcherWTraceAndNegation[MODEL],
              resolving_environment: FullResolvingEnvironment,
              input_: Callable[[FullResolvingEnvironment], MODEL]) -> MatchingResult:
        return primitive.matches_w_trace(input_(resolving_environment))

    def new_sdv_checker(self) -> LogicTypeSdvPropertiesChecker[MatcherWTraceAndNegation[MODEL]]:
        return self._sdv_checker

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker:
        return WithTreeStructureExecutionPropertiesChecker(MatcherDdv, MatcherWTraceAndNegation)
