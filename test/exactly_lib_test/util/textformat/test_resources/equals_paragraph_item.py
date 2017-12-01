import unittest

from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text, StringText, TextVisitor
from exactly_lib.util.textformat.structure.lists import HeaderContentList, HeaderContentListItem
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table
from exactly_lib.util.textformat.structure.utils import ParagraphItemVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources.structure import is_string_text


def equals_paragraph_items(expected_items: list) -> asrt.ValueAssertion:
    return asrt.equals_sequence(expected_items,
                                equals_paragraph_item)


def equals_paragraph_item(expected: ParagraphItem) -> asrt.ValueAssertion:
    return _EqualsParagraphItem(expected)


def equals_list_item(expected: HeaderContentListItem) -> asrt.ValueAssertion:
    return asrt.is_instance_with(HeaderContentListItem,
                                 asrt.and_([
                                     asrt.sub_component('header',
                                                        HeaderContentListItem.header.fget,
                                                        equals_text(expected.header)),
                                     asrt.sub_component('content_paragraph_items',
                                                        HeaderContentListItem.content_paragraph_items.fget,
                                                        equals_paragraph_items(expected.content_paragraph_items)),
                                 ]))


def equals_list_items(expected: list) -> asrt.ValueAssertion:
    return asrt.equals_sequence(expected,
                                equals_list_item)


def equals_list_format(expected: lists.Format) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        lists.Format,
        asrt.and_([
            asrt.sub_component('list_type',
                               lists.Format.list_type.fget,
                               asrt.equals(expected.list_type)
                               ),
            asrt.sub_component('custom_indent_spaces',
                               lists.Format.custom_indent_spaces.fget,
                               asrt.equals(expected.custom_indent_spaces)
                               ),
            asrt.sub_component('custom_separations',
                               lists.Format.custom_separations.fget,
                               asrt.equals(expected.custom_separations)
                               ),
        ]))


def equals_text(expected: Text) -> asrt.ValueAssertion:
    return _EqualsText(expected)


def equals_cross_reference_target(expected: core.CrossReferenceTarget) -> asrt.ValueAssertion:
    return asrt.is_instance(type(expected))


class _EqualsParagraphItem(asrt.ValueAssertion):
    def __init__(self, expected: ParagraphItem):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        checker = _EqualsParagraphItemVisitor(value,
                                              put,
                                              message_builder)
        checker.visit(self.expected)


class _EqualsText(asrt.ValueAssertion):
    def __init__(self, expected: Text):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        checker = _EqualsTextVisitor(value,
                                     put,
                                     message_builder)
        checker.visit(self.expected)


class _EqualsParagraphItemVisitor(ParagraphItemVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def visit_paragraph(self, expected: Paragraph):
        self._assert_is_type(Paragraph)
        actual = self.actual
        assert isinstance(actual, Paragraph)
        items_assertion = asrt.equals_sequence(expected.start_on_new_line_blocks,
                                               equals_text)
        items_assertion.apply(self.put,
                              actual.start_on_new_line_blocks,
                              self.message_builder.for_sub_component('start_on_new_line_blocks'))

        self.put.assertEqual(len(expected.start_on_new_line_blocks),
                             len(actual.start_on_new_line_blocks),
                             self._msg("Number of %s's in %s" % (Text, Paragraph)))
        text_index = 0
        for (expected_text, actual_text) in zip(expected.start_on_new_line_blocks,
                                                actual.start_on_new_line_blocks):
            self._assert_equal_text(expected_text, actual_text,
                                    'Text at index %d: ' % text_index)
            text_index += 1

    def visit_header_value_list(self, expected: HeaderContentList):
        self._assert_is_type(HeaderContentList)
        actual = self.actual
        assertions = asrt.is_instance_with(
            lists.HeaderContentList,
            asrt.and_([
                asrt.sub_component('list-format',
                                   lists.HeaderContentList.list_format.fget,
                                   equals_list_format(expected.list_format)
                                   ),
                asrt.sub_component('list-items',
                                   lists.HeaderContentList.items.fget,
                                   equals_list_items(expected.items)),
            ]

            ))
        assertions.apply(self.put,
                         actual,
                         self.message_builder)

    def visit_literal_layout(self, expected: LiteralLayout):
        self._assert_is_type(LiteralLayout)
        actual = self.actual
        assert isinstance(actual, LiteralLayout)
        self.put.assertEqual(expected.literal_text,
                             actual.literal_text)

    def visit_table(self, expected: Table):
        self.put.fail('Implementation error: tables not supported')

    def _msg(self, tail: str) -> str:
        return self.message_builder.apply(tail)

    def _assert_is_type(self, expected: type):
        self.put.assertIsInstance(self.actual,
                                  expected,
                                  self._msg('Expecting a %s' % expected))

    def _assert_equal_text(self,
                           expected_text, actual_text,
                           msg_tail: str):
        assert isinstance(expected_text, StringText)
        assert isinstance(actual_text, StringText)
        self.put.assertEqual(expected_text.value,
                             actual_text.value,
                             self._msg(msg_tail))


class _EqualsTextVisitor(TextVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def visit_string(self, expected: StringText):
        self._assert_is_type(StringText)
        actual = self.actual
        assert isinstance(actual, StringText)
        asrt.equals(expected.value).apply(self.put,
                                          actual.value,
                                          self.message_builder.for_sub_component('value'))

    def visit_cross_reference(self, expected: core.CrossReferenceText):
        self._assert_is_type(core.CrossReferenceText)
        actual = self.actual
        assert isinstance(actual, core.CrossReferenceText)

        assertion = asrt.is_instance_with(
            core.CrossReferenceText,
            asrt.and_([
                asrt.sub_component('title_text',
                                   core.CrossReferenceText.title_text.fget,
                                   equals_text(expected.title_text)),
                asrt.sub_component('target_is_id_in_same_document',
                                   core.CrossReferenceText.target_is_id_in_same_document.fget,
                                   asrt.equals(expected.target_is_id_in_same_document)),
                asrt.sub_component('target',
                                   core.CrossReferenceText.target.fget,
                                   equals_cross_reference_target(expected.target)),
            ]))

        assertion.apply(self.put, self.actual, self.message_builder)

    def visit_anchor(self, expected: core.AnchorText):
        self._assert_is_type(core.AnchorText)
        actual = self.actual
        assert isinstance(actual, core.AnchorText)

        equals_text(expected.anchored_text).apply(
            self.put,
            actual.anchored_text,
            self.message_builder.for_sub_component('anchored_text')
        )

        equals_cross_reference_target(expected.anchor).apply(
            self.put,
            actual.anchor,
            self.message_builder.for_sub_component('anchor'))

    def _msg(self, tail: str) -> str:
        return self.message_builder.apply(tail)

    def _assert_is_type(self, expected: type):
        self.put.assertIsInstance(self.actual,
                                  expected,
                                  self._msg('Expecting a %s' % expected))


def is_string_text_that_equals(expected: str) -> asrt.ValueAssertion:
    return asrt.And([
        is_string_text,
        asrt.sub_component('value',
                           core.StringText.value.fget,
                           asrt.equals(expected)),
    ])
