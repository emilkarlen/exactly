import unittest

from exactly_lib.util.line_source import Line, LineSequence
from exactly_lib_test.test_resources.assert_utils import assertion_message


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
                               assertion_message('Line expected to be None'))
    test_case.assertEqual(expected.line_number,
                          actual.line_number,
                          assertion_message('Line number', message_header))
    test_case.assertEqual(expected.text,
                          actual.text,
                          assertion_message('Line text', message_header))


def assert_equals_line_sequence(test_case: unittest.TestCase,
                                expected: LineSequence,
                                actual: LineSequence,
                                message_header: str=None):
    """
    :param expected: May be None
    :param actual: May be None
    :param message_header: Optional header for assert messages.
    """
    if expected is None:
        test_case.assertIsNone(actual,
                               assertion_message('Line expected to be None'))
    test_case.assertEqual(expected.first_line_number,
                          actual.first_line_number,
                          assertion_message('First line number', message_header))
    test_case.assertEqual(len(expected.lines),
                          len(actual.lines),
                          assertion_message('Number of lines', message_header))
    for line_idx, (e_line, a_line) in enumerate(zip(expected.lines, actual.lines)):
        test_case.assertEqual(e_line,
                              a_line,
                              assertion_message('Line text of line %d (0-based) in line-sequence' % line_idx,
                                                message_header))
