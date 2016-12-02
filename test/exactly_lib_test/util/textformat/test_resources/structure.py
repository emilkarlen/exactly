import unittest

from exactly_lib.util.textformat.structure import core, lists, document as doc
from exactly_lib.util.textformat.structure.lists import HeaderContentList
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table, TableFormat
from exactly_lib.util.textformat.structure.utils import ParagraphItemVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def is_paragraph_item_list(name: str = '') -> va.ValueAssertion:
    return va.every_element(name, is_paragraph_item)


is_string_text = va.is_instance_with(core.StringText,
                                     va.sub_component('value',
                                                      core.StringText.value.fget,
                                                      va.IsInstance(str)))

is_cross_reference_text = va.is_instance_with(core.CrossReferenceText,
                                              va.And([
                                                  va.sub_component('target',
                                                                   core.CrossReferenceText.target.fget,
                                                                   va.IsInstance(core.CrossReferenceTarget)),
                                                  va.sub_component('title',
                                                                   core.CrossReferenceText.title.fget,
                                                                   va.IsInstance(str))
                                              ]))


def is_cross_reference_target_list(name: str = '') -> va.ValueAssertion:
    return va.every_element(name, is_cross_reference_target)


is_cross_reference_target = va.IsInstance(core.CrossReferenceTarget)

is_concrete_text = va.Or([
    is_string_text,
    is_cross_reference_text,
])

is_anchor_text = va.is_instance_with(
    core.AnchorText,
    va.And([
        va.sub_component('anchor',
                         core.AnchorText.anchor.fget,
                         va.IsInstance(core.CrossReferenceTarget)),
        va.sub_component('anchored_text',
                         core.AnchorText.anchored_text.fget,
                         is_concrete_text)
    ]))

is_text = va.Or([
    is_concrete_text,
    is_anchor_text,
])


class _IsParagraphItem(ParagraphItemVisitor, va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        self.put = put
        self.message_builder = message_builder
        self.visit(value)

    def visit_paragraph(self, paragraph: Paragraph):
        is_paragraph.apply(self.put, paragraph, self.message_builder)

    def visit_header_value_list(self, header_value_list: HeaderContentList):
        is_header_value_list.apply(self.put, header_value_list, self.message_builder)

    def visit_literal_layout(self, literal_layout: LiteralLayout):
        assertion = va.sub_component('literal_layout/literal_text',
                                     LiteralLayout.literal_text.fget,
                                     va.IsInstance(str))
        assertion.apply(self.put, literal_layout, self.message_builder)

    def visit_table(self, table: Table):
        format_assertion = va.sub_component('format',
                                            Table.format.fget,
                                            va.IsInstance(TableFormat))
        is_table_row = va.every_element('table row cells',
                                        is_paragraph_item_list())
        rows_assertion = va.sub_component_list('rows', Table.rows.fget, is_table_row, '/')

        assertion = va.And([format_assertion,
                            rows_assertion])

        assertion.apply(self.put, table, self.message_builder)


is_paragraph_item = _IsParagraphItem()

is_paragraph = va.And([
    va.IsInstance(Paragraph),
    va.sub_component_list('text blocks',
                          lambda p: p.start_on_new_line_blocks,
                          is_text)])


class SectionAssertion:
    def is_section_contents(self,
                            put: unittest.TestCase,
                            value,
                            message_builder: va.MessageBuilder = va.MessageBuilder()):
        va.And([
            va.IsInstance(doc.SectionContents),
            va.sub_component_list('initial_paragraphs',
                                  doc.SectionContents.initial_paragraphs.fget,
                                  is_paragraph_item)
        ]).apply(put, value, message_builder)
        assert isinstance(value, doc.SectionContents)
        sections_message = va.sub_component_builder('sections', message_builder)
        va.IsInstance(list).apply(put, value.sections, sections_message)
        for (idx, section) in enumerate(value.sections):
            self.is_section(put, section,
                            va.sub_component_builder('[%d]' % idx, sections_message))

    def is_section(self,
                   put: unittest.TestCase,
                   value,
                   message_builder: va.MessageBuilder = va.MessageBuilder()):
        va.IsInstance(doc.Section).apply(put, value, message_builder)
        assert isinstance(value, doc.Section)
        va.sub_component('header',
                         doc.Section.header.fget,
                         is_text).apply(put, value, message_builder)
        self.is_section_contents(put, value.contents,
                                 va.sub_component_builder('contents', message_builder))


SECTION_ASSERTION = SectionAssertion()

is_section_contents = va.OfCallable(SECTION_ASSERTION.is_section_contents)

is_section = va.OfCallable(SECTION_ASSERTION.is_section)

is_list_item = va.And([
    va.IsInstance(lists.HeaderContentListItem),
    va.sub_component('header',
                     lists.HeaderContentListItem.header.fget,
                     is_text),
    va.sub_component_list('values',
                          lists.HeaderContentListItem.content_paragraph_items.fget,
                          is_paragraph_item)
])

is_separations = va.IsInstance(lists.Separations)

is_list_format = va.And([
    va.IsInstance(lists.Format),
    va.sub_component('list_type',
                     lists.Format.list_type.fget,
                     va.IsInstance(lists.ListType)),
    va.sub_component('custom_indent_spaces',
                     lists.Format.custom_indent_spaces.fget,
                     va.optional(va.IsInstance(int))),
    va.sub_component('custom_separations',
                     lists.Format.custom_separations.fget,
                     va.optional(is_separations)),
])

is_header_value_list = va.And([
    va.IsInstance(lists.HeaderContentList),
    va.sub_component('format',
                     lists.HeaderContentList.list_format.fget,
                     is_list_format),
    va.sub_component_list('items',
                          lists.HeaderContentList.items.fget,
                          is_list_item),
])
