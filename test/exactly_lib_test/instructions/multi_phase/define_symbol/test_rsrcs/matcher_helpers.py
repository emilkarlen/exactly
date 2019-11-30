import unittest
from abc import ABC, abstractmethod

from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder


class AssertApplicationOfMatcherInSymbolTable(ValueAssertionBase[InstructionEnvironmentForPostSdsStep], ABC):
    def __init__(self,
                 matcher_symbol_name: str,
                 expected_matcher_result: ValueAssertion[MatchingResult]):
        self.matcher_symbol_name = matcher_symbol_name
        self.expected_matcher_result = expected_matcher_result

    def _apply(self,
               put: unittest.TestCase,
               value: InstructionEnvironmentForPostSdsStep,
               message_builder: MessageBuilder):
        result = self._apply_matcher(value)

        self.expected_matcher_result.apply_with_message(put, result, 'matching result')

    @abstractmethod
    def _apply_matcher(self, environment: InstructionEnvironmentForPostSdsStep) -> MatchingResult:
        pass
