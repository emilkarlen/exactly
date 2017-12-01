import unittest

from exactly_lib.util.textformat.structure import core, lists, document as doc
from exactly_lib.util.textformat.structure.lists import HeaderContentList
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table, TableFormat, TableCell
from exactly_lib.util.textformat.structure.utils import ParagraphItemVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_paragraph_item_list(name: str = '') -> asrt.ValueAssertion:
    return asrt.every_element(name, is_paragraph_item)


is_tags_set = asrt.is_instance_with(set,
                                    asrt.every_element('set of tags', asrt.is_instance(str)))

is_string_text = asrt.is_instance_with(core.StringText,
                                       asrt.and_([
                                           asrt.sub_component('value',
                                                              core.StringText.value.fget,
                                                              asrt.IsInstance(str)),

                                           asrt.sub_component('tags',
                                                              core.StringText.tags.fget,
                                                              is_tags_set),
                                       ]))

is_cross_reference_text = asrt.is_instance_with(core.CrossReferenceText,
                                                asrt.And([
                                                    asrt.sub_component('target',
                                                                       core.CrossReferenceText.target.fget,
                                                                       asrt.IsInstance(core.CrossReferenceTarget)),
                                                    asrt.sub_component('title',
                                                                       core.CrossReferenceText.title_text.fget,
                                                                       is_string_text),

                                                    asrt.sub_component('tags',
                                                                       core.CrossReferenceText.tags.fget,
                                                                       is_tags_set),
                                                ]))


def is_cross_reference_target_list(name: str = '') -> asrt.ValueAssertion:
    return asrt.every_element(name, is_cross_reference_target)


is_cross_reference_target = asrt.IsInstance(core.CrossReferenceTarget)

is_concrete_text = asrt.Or([
    is_string_text,
    is_cross_reference_text,
])

is_anchor_text = asrt.is_instance_with(
    core.AnchorText,
    asrt.And([
        asrt.sub_component('anchor',
                           core.AnchorText.anchor.fget,
                           asrt.IsInstance(core.CrossReferenceTarget)),
        asrt.sub_component('anchored_text',
                           core.AnchorText.anchored_text.fget,
                           is_concrete_text),
        asrt.sub_component('tags',
                           core.AnchorText.tags.fget,
                           is_tags_set),
    ]))

is_text = asrt.Or([
    is_concrete_text,
    is_anchor_text,
])


class _IsParagraphItem(ParagraphItemVisitor, asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        self.put = put
        self.message_builder = message_builder
        self.visit(value)

    def visit_paragraph(self, paragraph: Paragraph):
        is_paragraph.apply(self.put, paragraph, self.message_builder)

    def visit_header_value_list(self, header_value_list: HeaderContentList):
        is_header_value_list.apply(self.put, header_value_list, self.message_builder)

    def visit_literal_layout(self, literal_layout: LiteralLayout):
        assertion = asrt.sub_component('literal_layout/literal_text',
                                       LiteralLayout.literal_text.fget,
                                       asrt.IsInstance(str))
        assertion.apply(self.put, literal_layout, self.message_builder)

    def visit_table(self, table: Table):
        format_assertion = asrt.sub_component('format',
                                              Table.format.fget,
                                              asrt.IsInstance(TableFormat))
        is_table_row = asrt.every_element('table row cells',
                                          is_table_cell)
        rows_assertion = asrt.sub_component_list('rows', Table.rows.fget, is_table_row, '/')

        assertion = asrt.And([format_assertion,
                              rows_assertion])

        assertion.apply(self.put, table, self.message_builder)


is_paragraph_item = _IsParagraphItem()

is_table_cell = asrt.is_instance_with(TableCell,
                                      asrt.sub_component('paragraph items of cell',
                                                         TableCell.paragraph_items.fget,
                                                         is_paragraph_item_list()))

is_paragraph = asrt.And([
    asrt.IsInstance(Paragraph),
    asrt.sub_component_list('text blocks',
                            lambda p: p.start_on_new_line_blocks,
                            is_text)])


class SectionAssertion:
    def is_section_contents(self,
                            put: unittest.TestCase,
                            value,
                            message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        asrt.And([
            asrt.IsInstance(doc.SectionContents),
            asrt.sub_component_list('initial_paragraphs',
                                    doc.SectionContents.initial_paragraphs.fget,
                                    is_paragraph_item)
        ]).apply(put, value, message_builder)
        assert isinstance(value, doc.SectionContents)
        sections_message = asrt.sub_component_builder('sections', message_builder)
        asrt.IsInstance(list).apply(put, value.sections, sections_message)
        for (idx, section) in enumerate(value.sections):
            self.is_section_item(put, section,
                                 asrt.sub_component_builder('[%d]' % idx, sections_message))

    def is_section_item(self,
                        put: unittest.TestCase,
                        value,
                        message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        asrt.IsInstance(doc.SectionItem).apply(put, value, message_builder)
        assert isinstance(value, doc.SectionItem)
        asrt.sub_component('header',
                           doc.SectionItem.header.fget,
                           is_text).apply(put, value, message_builder)
        if isinstance(value, doc.Article):
            is_article_contents.apply(put, value.contents,
                                      message_builder.for_sub_component('article_contents'))
        elif isinstance(value, doc.Section):
            is_section_contents.apply(put, value.contents,
                                      message_builder.for_sub_component('section_contents'))
        else:
            asrt.fail('Not a {}: {}'.format(str(doc.SectionItem), str(value)))


SECTION_ASSERTION = SectionAssertion()

is_section_contents = asrt.OfCallable(SECTION_ASSERTION.is_section_contents)

is_article_contents = asrt.is_instance_with(
    doc.ArticleContents,
    asrt.and_([
        asrt.sub_component_list('abstract_paragraphs',
                                doc.ArticleContents.abstract_paragraphs.fget,
                                is_paragraph_item),
        asrt.sub_component('section_contents',
                           doc.ArticleContents.section_contents.fget,
                           is_section_contents)
    ]))

is_section_item = asrt.OfCallable(SECTION_ASSERTION.is_section_item)

is_list_item = asrt.And([
    asrt.IsInstance(lists.HeaderContentListItem),
    asrt.sub_component('header',
                       lists.HeaderContentListItem.header.fget,
                       is_text),
    asrt.sub_component_list('values',
                            lists.HeaderContentListItem.content_paragraph_items.fget,
                            is_paragraph_item)
])

is_separations = asrt.IsInstance(lists.Separations)

is_list_format = asrt.And([
    asrt.IsInstance(lists.Format),
    asrt.sub_component('list_type',
                       lists.Format.list_type.fget,
                       asrt.IsInstance(lists.ListType)),
    asrt.sub_component('custom_indent_spaces',
                       lists.Format.custom_indent_spaces.fget,
                       asrt.optional(asrt.IsInstance(int))),
    asrt.sub_component('custom_separations',
                       lists.Format.custom_separations.fget,
                       asrt.optional(is_separations)),
])

is_header_value_list = asrt.And([
    asrt.IsInstance(lists.HeaderContentList),
    asrt.sub_component('format',
                       lists.HeaderContentList.list_format.fget,
                       is_list_format),
    asrt.sub_component_list('items',
                            lists.HeaderContentList.items.fget,
                            is_list_item),
])
