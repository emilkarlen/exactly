import unittest

import re

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def is_empty() -> ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return asrt.Equals('')


def is_not_only_space() -> ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _IS_NOT_ONLY_SPACE


def begins_with(expected: str) -> ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _BeginsWith(expected)


def contains(expected: str) -> ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _Contains(expected)


class _BeginsWith(ValueAssertionBase):
    def __init__(self, initial: str):
        self.initial = initial

    def _apply(self,
               put: unittest.TestCase,
               value: str,
               message_builder: asrt.MessageBuilder):
        actual = value[:len(self.initial)]
        put.assertEqual(self.initial,
                        actual,
                        message_builder.apply('Initial characters of string.'))


class _Contains(ValueAssertionBase):
    def __init__(self, part: str):
        self.part = part

    def _apply(self,
               put: unittest.TestCase,
               value: str,
               message_builder: asrt.MessageBuilder):
        put.assertTrue(value.find(self.part) != -1,
                       message_builder.apply("contains string '{}'".format(self.part))
                       )


class _IsNotOnlySpace(ValueAssertionBase):
    _NON_SPACE_RE = re.compile('\\S')

    def _apply(self,
               put: unittest.TestCase,
               value: str,
               message_builder: asrt.MessageBuilder):
        match = self._NON_SPACE_RE.search(value)
        if match is None:
            put.fail(message_builder.apply('No non-space character found.'))


_IS_NOT_ONLY_SPACE = _IsNotOnlySpace()


def first_line(assertion: ValueAssertion[str]) -> ValueAssertion[str]:
    return asrt.on_transformed(
        get_first_line,
        assertion
    )


def get_first_line(s: str) -> str:
    return s.splitlines()[0]
