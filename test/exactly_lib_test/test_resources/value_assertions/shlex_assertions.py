import shlex
import unittest

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder


def matches_single_quotes_str(unquoted: ValueAssertion[str]) -> ValueAssertion[str]:
    return _SingleQuotedStr(unquoted)


class _SingleQuotedStr(ValueAssertionBase[str]):
    def __init__(self, unquoted: ValueAssertion[str]):
        self._unquoted = unquoted

    def _apply(self,
               put: unittest.TestCase,
               value: str,
               message_builder: MessageBuilder,
               ):
        unquoted = shlex.split(value)
        num_quoted_elements = asrt.len_equals(1)
        num_quoted_elements.apply(
            put,
            unquoted,
            message_builder.for_sub_component('number of quoted elements')
        )
        self._unquoted.apply(
            put,
            unquoted[0],
            message_builder.for_sub_component('unquoted')
        )
