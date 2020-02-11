import unittest
from typing import TypeVar, Generic, Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.logic_base_class import LogicDdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv, MatchingResult
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.logic.test_resources.custom_properties_checker import \
    CustomExecutionPropertiesChecker, CustomPropertiesCheckerConfiguration
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicTypeSdvPropertiesChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertion
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree

MODEL = TypeVar('MODEL')

ModelConstructor = Callable[[FullResolvingEnvironment], MODEL]


class _MatcherExecutionPropertiesChecker(Generic[MODEL],
                                         CustomExecutionPropertiesChecker[MatcherWTraceAndNegation[MODEL]]
                                         ):
    def __init__(self):
        self._structure_tree_of_ddv = None

    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: LogicDdv[MatcherWTraceAndNegation[MODEL]],
                  message_builder: MessageBuilder,
                  ):
        asrt.is_instance(MatcherDdv).apply(put, actual, message_builder.for_sub_component('object type'))

        assert isinstance(actual, MatcherDdv)  # Type info for IDE

        self._structure_tree_of_ddv = actual.structure().render()

        asrt_d_tree.matches_node().apply(
            put,
            self._structure_tree_of_ddv,
            message_builder.for_sub_component('sanity of structure'),
        )

    def check_primitive(self,
                        put: unittest.TestCase,
                        actual: MatcherWTraceAndNegation[MODEL],
                        message_builder: MessageBuilder,
                        ):
        asrt.is_instance(MatcherWTraceAndNegation).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        self._check_structure(put, actual, message_builder)

    def _check_structure(self,
                         put: unittest.TestCase,
                         actual: MatcherWTraceAndNegation[MODEL],
                         message_builder: MessageBuilder,
                         ):
        structure_tree_of_primitive = actual.structure().render()

        asrt_d_tree.matches_node().apply(
            put,
            structure_tree_of_primitive,
            message_builder.for_sub_component('sanity of structure'),
        )

        structure_equals_ddv = asrt_d_tree.header_data_and_children_equal_as(self._structure_tree_of_ddv)

        structure_equals_ddv.apply_with_message(
            put,
            structure_tree_of_primitive,
            'structure of should be same as that of ddv',
        )


class MatcherPropertiesCheckerConfiguration(Generic[MODEL],
                                            CustomPropertiesCheckerConfiguration[MatcherWTraceAndNegation[MODEL],
                                                                                 Callable[
                                                                                     [FullResolvingEnvironment], MODEL],
                                                                                 ValueAssertion[MatchingResult]]
                                            ):
    def __init__(self, expected_logic_value_type: LogicValueType):
        self._sdv_checker = LogicTypeSdvPropertiesChecker(expected_logic_value_type)

    def apply(self,
              primitive: MatcherWTraceAndNegation[MODEL],
              resolving_environment: FullResolvingEnvironment,
              input_: Callable[[FullResolvingEnvironment], MODEL]) -> MatchingResult:
        return primitive.matches_w_trace(input_(resolving_environment))

    def new_sdv_checker(self) -> LogicTypeSdvPropertiesChecker[MatcherWTraceAndNegation[MODEL]]:
        return self._sdv_checker

    def new_execution_checker(self) -> _MatcherExecutionPropertiesChecker:
        return _MatcherExecutionPropertiesChecker()
