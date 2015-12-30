import unittest


def assertion_message(message: str,
                      header: str=None):
    return message if not header else header + ': ' + message


class MessageWithHeaderConstructor:
    def __init__(self,
                 header: str=None):
        self.header = header

    def msg(self, message: str) -> str:
        return assertion_message(message, self.header)


class TestCaseWithMessageHeader:
    def __init__(self,
                 test_case: unittest.TestCase,
                 msg_constructor: MessageWithHeaderConstructor):
        self._test_case = test_case
        self._msg_constructor = msg_constructor

    @property
    def tc(self) -> unittest.TestCase:
        return self._test_case

    @property
    def message_header(self) -> str:
        return self._msg_constructor.header

    def msg(self, message: str) -> str:
        return self._msg_constructor.msg(message)


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
