import unittest

from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder


class LineMatcherModelIsValid(ValueAssertionBase[LineMatcherLine]):
    def _apply(self,
               put: unittest.TestCase,
               value: LineMatcherLine,
               message_builder: MessageBuilder,
               ):
        line_num_msg_builder = message_builder.for_sub_component('line-num')

        line_num = value[0]
        put.assertIsInstance(line_num, int,
                             line_num_msg_builder.apply('type'))
        put.assertGreaterEqual(line_num, 1,
                               line_num_msg_builder.apply('value'))

        contents_msg_builder = message_builder.for_sub_component('contents')

        contents = value[1]
        put.assertIsInstance(contents, str,
                             contents_msg_builder.apply('type'))
        if contents.find('\n') != -1:
            put.fail(contents_msg_builder.apply('Line contents contains new-line: ' + repr(value)))


def validated(model: LineMatcherLine) -> LineMatcherLine:
    line_num = model[0]
    if not isinstance(line_num, int):
        raise ValueError('Line number is not an int: ' + repr(model))
    if line_num <= 0:
        raise ValueError('Line number is <= 0: ' + repr(model))

    contents = model[1]
    if not isinstance(contents, str):
        raise ValueError('Line contents is not an str: ' + repr(model))
    if contents.find('\n') != -1:
        raise ValueError('Line contents contains new-line: ' + repr(model))

    return model
