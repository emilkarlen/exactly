import unittest
from typing import TypeVar, Generic, Callable

from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.sdv_checker import \
    FullDepsSdvPropertiesChecker, \
    WithNodeDescriptionExecutionPropertiesChecker
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result

MODEL = TypeVar('MODEL')

ModelConstructor = Callable[[FullResolvingEnvironment], MODEL]


class MatcherPropertiesConfiguration(
    Generic[MODEL],
    CommonPropertiesConfiguration[MatcherWTrace[MODEL],
                                  Callable[[FullResolvingEnvironment], MODEL],
                                  MatchingResult]):
    def __init__(self):
        self._sdv_checker = FullDepsSdvPropertiesChecker(MatcherSdv)
        self._applier = _MatcherApplier()

    def applier(self) -> Applier[MatcherWTrace[MODEL],
                                 Callable[[FullResolvingEnvironment], MODEL],
                                 MatchingResult]:
        return self._applier

    def new_sdv_checker(self) -> FullDepsSdvPropertiesChecker[MatcherWTrace[MODEL]]:
        return self._sdv_checker

    def new_execution_checker(self) -> WithNodeDescriptionExecutionPropertiesChecker[MatchingResult]:
        return WithNodeDescriptionExecutionPropertiesChecker(MatcherDdv,
                                                             MatcherWTrace,
                                                             asrt_matching_result.matches())


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
