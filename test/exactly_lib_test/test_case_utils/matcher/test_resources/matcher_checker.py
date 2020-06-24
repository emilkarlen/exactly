import unittest
from typing import TypeVar, Generic, Callable

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, \
    MatcherWTrace
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder

MODEL = TypeVar('MODEL')

ModelConstructor = Callable[[FullResolvingEnvironment], MODEL]


class MatcherPropertiesConfiguration(
    Generic[MODEL],
    CommonPropertiesConfiguration[MatcherWTrace[MODEL],
                                  Callable[[FullResolvingEnvironment], MODEL],
                                  MatchingResult]):
    def __init__(self):
        self._sdv_checker = LogicSdvPropertiesChecker(MatcherSdv)
        self._applier = _MatcherApplier()

    def applier(self) -> Applier[MatcherWTrace[MODEL],
                                 Callable[[FullResolvingEnvironment], MODEL],
                                 MatchingResult]:
        return self._applier

    def new_sdv_checker(self) -> LogicSdvPropertiesChecker[MatcherWTrace[MODEL]]:
        return self._sdv_checker

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker:
        return WithTreeStructureExecutionPropertiesChecker(MatcherDdv, MatcherWTrace)


class _MatcherApplier(
    Generic[MODEL],
    Applier[MatcherWTrace[MODEL], Callable[[FullResolvingEnvironment], MODEL], MatchingResult]
):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: MatcherWTrace[MODEL],
              resolving_environment: FullResolvingEnvironment,
              input_: Callable[[FullResolvingEnvironment], MODEL]) -> MatchingResult:
        return primitive.matches_w_trace(input_(resolving_environment))
