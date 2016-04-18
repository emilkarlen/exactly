import re
import unittest

from shellcheck_lib_test.test_resources import value_assertion as va


def is_empty() -> va.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return va.Equals('')


def is_not_only_space() -> va.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _IS_NOT_ONLY_SPACE


def begins_with(expected: str) -> va.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return _BeginsWith(expected)


class _BeginsWith(va.ValueAssertion):
    def __init__(self, initial: str):
        self.initial = initial

    def apply(self,
              put: unittest.TestCase,
              value: str,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        actual = value[:len(self.initial)]
        put.assertEqual(self.initial,
                        actual,
                        'Initial characters of string.')


class _IsNotOnlySpace(va.ValueAssertion):
    _NON_SPACE_RE = re.compile('\\S')

    def apply(self,
              put: unittest.TestCase,
              value: str,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        match = self._NON_SPACE_RE.search(value)
        if match is None:
            put.fail('No non-space character found.')

_IS_NOT_ONLY_SPACE = _IsNotOnlySpace()

