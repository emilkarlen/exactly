__author__ = 'emil'

import unittest


def assertion_message(message: str,
                      header: str=None):
    return message if not header else header + ': ' + message


def assert_is_none_or_equals(test_case: unittest.TestCase,
                             expected,
                             actual,
                             item: str=None):
    """

    :param expected: If None, then the actual value is checked for None.
     Otherwise, equals.
    :param actual:
    :param item: Name/description of checked item for assertion message.
    :return:
    """
    if expected is None:
        test_case.assertIsNone(actual,
                               assertion_message('Expected to be None', item))
    else:
        test_case.assertIsNotNone(actual,
                                  assertion_message('Expected to NOT be None', item))
        test_case.assertEqual(actual,
                              expected,
                              item)
