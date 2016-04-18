import unittest

from shellcheck_lib_test.test_resources import value_assertion as va


def is_empty() -> va.ValueAssertion:
    """
    :rtype: An Assertion on a str.
    """
    return va.Equals('')


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
