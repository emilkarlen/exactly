import unittest

from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder


class AssertApplicationOfMatcherInSymbolTable(ValueAssertionBase[InstructionEnvironmentForPostSdsStep], ABC):
    def __init__(self,
                 matcher_symbol_name: str,
                 expected_matcher_result: Optional[ValueAssertion[str]]):
        self.matcher_symbol_name = matcher_symbol_name
        self.expected_matcher_result = expected_matcher_result

    def _apply(self,
               put: unittest.TestCase,
               value: InstructionEnvironmentForPostSdsStep,
               message_builder: MessageBuilder):
        result = self._apply_matcher(value)

        check_result(put, value,
                     self.expected_matcher_result,
                     result)

    @abstractmethod
    def _apply_matcher(self,
                       environment: InstructionEnvironmentForPostSdsStep) -> Optional[ErrorMessageResolver]:
        pass


def check_result(put: unittest.TestCase,
                 environment: InstructionEnvironmentForPostSdsStep,
                 expected_matcher_result: Optional[ValueAssertion[str]],
                 actual_result: Optional[ErrorMessageResolver]):
    if expected_matcher_result is None:
        put.assertIsNone(actual_result,
                         'result from main')
    else:
        put.assertIsNotNone(actual_result,
                            'result from main')
        err_msg_env = ErrorMessageResolvingEnvironment(environment.home_and_sds,
                                                       environment.symbols)
        err_msg = actual_result.resolve(err_msg_env)
        expected_matcher_result.apply_with_message(put, err_msg,
                                                   'error result of main')
