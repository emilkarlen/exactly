__author__ = 'emil'

import unittest

from shelltest.phase_instr.line_source import Line


def assert_equals_line(test_case: unittest.TestCase,
                       expected: Line,
                       actual: Line,
                       message_header: str=None):
    """
    :param expected: May be None
    :param actual: May be None
    :param message_header: Optional header for assert messages.
    """
    if expected is None:
        test_case.assertIsNone(actual,
                               _message('Line expected to be None'))
    test_case.assertEqual(expected.line_number,
                          actual.line_number,
                          _message('Line number', message_header))
    test_case.assertEqual(expected.text,
                          actual.text,
                          _message('Line text', message_header))
