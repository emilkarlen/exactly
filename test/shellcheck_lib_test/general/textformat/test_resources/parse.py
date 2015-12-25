import unittest

from shellcheck_lib.general.textformat.structure.core import ParagraphItem, Text
from shellcheck_lib.general.textformat.structure.lists import HeaderValueList
from shellcheck_lib.general.textformat.structure.paragraph import Paragraph
from shellcheck_lib.general.textformat.structure.utils import ParagraphItemVisitor
from shellcheck_lib_test.general.textformat.test_resources import structure as structure_assert


class Setup(tuple):
    def __new__(cls, source_lines: list,
                expected_paragraph_items: list):
        return tuple.__new__(cls, (source_lines,
                                   expected_paragraph_items))

    @property
    def source_lines(self) -> list:
        return self[0]

    @property
    def expected_paragraph_items(self) -> list:
        return self[1]


def check(put: unittest.TestCase,
          expected_items: list,
          actual_items: list):
    structure_assert.paragraph_item_list(put, expected_items, 'Hardcoded Expected value: ')
    structure_assert.paragraph_item_list(put, actual_items, 'Actual value: ')
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
            assert isinstance(expected_text, Text)
            assert isinstance(actual_text, Text)
            self.put.assertEqual(expected_text.value,
                                 actual_text.value,
                                 self._msg('Text at index %d: ' % text_index))
            text_index += 1

    def visit_header_value_list(self, header_value_list: HeaderValueList):
        raise ValueError(self._msg("Cannot check %s's" % HeaderValueList))

    def _msg(self, tail: str) -> str:
        return self.msg_prefix + tail
