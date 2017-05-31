import re
import unittest

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_empty() -> asrt.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return asrt.Equals('')


def is_not_only_space() -> asrt.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _IS_NOT_ONLY_SPACE


def begins_with(expected: str) -> asrt.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _BeginsWith(expected)


def contains(expected: str) -> asrt.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _Contains(expected)


class _BeginsWith(asrt.ValueAssertion):
    def __init__(self, initial: str):
        self.initial = initial

    def apply(self,
              put: unittest.TestCase,
              value: str,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        actual = value[:len(self.initial)]
        put.assertEqual(self.initial,
                        actual,
                        'Initial characters of string.')


class _Contains(asrt.ValueAssertion):
    def __init__(self, part: str):
        self.part = part

    def apply(self,
              put: unittest.TestCase,
              value: str,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertTrue(value.find(self.part) != -1,
                       "contains string '{}'".format(self.part))


class _IsNotOnlySpace(asrt.ValueAssertion):
    _NON_SPACE_RE = re.compile('\\S')

    def apply(self,
              put: unittest.TestCase,
              value: str,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        match = self._NON_SPACE_RE.search(value)
        if match is None:
            put.fail('No non-space character found.')


_IS_NOT_ONLY_SPACE = _IsNotOnlySpace()
