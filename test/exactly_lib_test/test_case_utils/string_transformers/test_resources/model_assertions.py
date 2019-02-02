import unittest

from typing import List

from exactly_lib.type_system.logic.string_transformer import StringTransformerModel
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def model_as_list_matches(expected: ValueAssertion[List[str]]) -> ValueAssertion[StringTransformerModel]:
    return _ModelAsListMatches(expected)


class _ModelAsListMatches(asrt.ValueAssertionBase[StringTransformerModel]):
    def __init__(self, expected: ValueAssertion[List[str]]):
        self._expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: StringTransformerModel,
               message_builder: asrt.MessageBuilder):
        actual = list(value)
        self._expected.apply(put, actual, message_builder)
