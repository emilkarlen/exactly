import unittest
from typing import Generic

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv, LogicTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherTypeSdv
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.logic.test_resources import assertions as asrt_logic
from exactly_lib_test.test_case_utils.logic.test_resources.custom_properties_checker import \
    CustomSdvPropertiesChecker, PRIMITIVE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


class LogicTypeSdvPropertiesChecker(Generic[PRIMITIVE],
                                    CustomSdvPropertiesChecker[PRIMITIVE]):
    def __init__(self, expected_logic_value_type: LogicValueType):
        self._expected_logic_value_type = expected_logic_value_type
        self._is_valid_sdv = asrt_logic.matches_logic_sdv_attributes(
            MatcherTypeSdv,
            self._expected_logic_value_type,
            asrt.anything_goes()
        )

    def check(self,
              put: unittest.TestCase,
              actual: LogicSdv[PRIMITIVE],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(LogicTypeSdv).apply(put,
                                             actual,
                                             message_builder.for_sub_component('type'))
        assert isinstance(actual, LogicTypeSdv)  # Type info for IDE
        self._is_valid_sdv.apply(put, actual, message_builder)
