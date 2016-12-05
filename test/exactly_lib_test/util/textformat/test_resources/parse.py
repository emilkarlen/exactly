import unittest

from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text, StringText
from exactly_lib.util.textformat.structure.lists import HeaderContentList
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.utils import ParagraphItemVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.util.textformat.test_resources import structure as structure_assert


def check(put: unittest.TestCase,
          expected_items: list,
          actual_items: list):
    va.every_element('Hardcoded Expected value: ', structure_assert.is_paragraph_item).apply(put, expected_items)
    va.every_element('Actual value: ', structure_assert.is_paragraph_item).apply(put, actual_items)
    put.assertEqual(len(expected_items),
                    len(actual_items),
                    'Number of Paragraph Items')
    element_index = 0
    for (expected_item, actual_item) in zip(expected_items, actual_items):
        msg_prefix = 'Paragraph at index %d: ' % element_index
        item_checker = ParagraphItemChecker(put, msg_prefix, actual_item)
        item_checker.visit(expected_item)
        element_index += 1


class ParagraphItemChecker(ParagraphItemVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 msg_prefix: str,
                 actual: ParagraphItem):
        self.put = put
        self.msg_prefix = msg_prefix
        self.actual = actual

    def visit_paragraph(self, paragraph: Paragraph):
        actual = self.actual
        self.put.assertIsInstance(actual,
                                  Paragraph,
                                  self._msg('Expecting a %s' % Paragraph))
        assert isinstance(actual, Paragraph)
        self.put.assertEqual(len(paragraph.start_on_new_line_blocks),
                             len(actual.start_on_new_line_blocks),
                             self._msg("Number of %s's in %s" % (Text, Paragraph)))
        text_index = 0
        for (expected_text, actual_text) in zip(paragraph.start_on_new_line_blocks, actual.start_on_new_line_blocks):
            self._assert_equal_text(expected_text, actual_text,
                                    'Text at index %d: ' % text_index)
            text_index += 1

    def visit_header_value_list(self, header_value_list: HeaderContentList):
        put = self.put
        actual = self.actual
        _msg = self._msg
        structure_assert.is_header_value_list.apply_with_message(put, actual, self.msg_prefix)
        assert isinstance(actual, lists.HeaderContentList)
        put.assertIs(header_value_list.list_format.list_type,
                     actual.list_format.list_type,
                     _msg('List type is expected to be ' + str(header_value_list.list_format.list_type)))
        put.assertEqual(len(header_value_list.items),
                        len(actual.items),
                        _msg('Number of list items'))
        item_index = 0
        for expected_item, actual_item in zip(header_value_list.items, actual.items):
            self._assert_equal_text(expected_item.header,
                                    actual_item.header,
                                    'Item at index ' + str(item_index))
            put.assertFalse(list(actual_item.content_paragraph_items),
                            _msg('Item at index {}: content_paragraph_items should be empty'.format(item_index)))
            item_index += 1

    def visit_literal_layout(self, literal_layout: LiteralLayout):
        actual = self.actual
        self.put.assertIsInstance(actual,
                                  LiteralLayout,
                                  self._msg('Expecting a %s' % LiteralLayout))
        assert isinstance(actual, LiteralLayout)
        self.put.assertEqual(literal_layout.literal_text,
                             actual.literal_text)

    def _msg(self, tail: str) -> str:
        return self.msg_prefix + tail

    def _assert_equal_text(self,
                           expected_text, actual_text,
                           msg_tail: str):
        assert isinstance(expected_text, StringText)
        assert isinstance(actual_text, StringText)
        self.put.assertEqual(expected_text.value,
                             actual_text.value,
                             self._msg(msg_tail))
