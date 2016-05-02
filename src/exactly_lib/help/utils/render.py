from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc, lists, table
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.structures import simple_header_only_list


class RenderingEnvironment(tuple):
    def __new__(cls, cross_ref_text_constructor: CrossReferenceTextConstructor,
                render_simple_header_value_lists_as_tables: bool = False):
        return tuple.__new__(cls, (cross_ref_text_constructor,
                                   render_simple_header_value_lists_as_tables))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]

    @property
    def render_simple_header_value_lists_as_tables(self) -> bool:
        return self[1]


class SectionContentsRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        raise NotImplementedError()


def cross_reference_list(cross_references: list,
                         environment: RenderingEnvironment) -> ParagraphItem:
    """
    :type cross_references: [CrossReferenceTarget]
    :return: A ParagraphItem that displays a list of cross references.
    """
    return simple_header_only_list([environment.cross_ref_text_constructor.apply(cross_ref)
                                    for cross_ref in cross_references],
                                   lists.ListType.ITEMIZED_LIST)


def transform_list_to_table(l: lists.HeaderContentList) -> table.Table:
    rows = []
    for item in l.items:
        assert isinstance(item, lists.HeaderContentListItem)
        header_cell = [Paragraph([item.header])]
        value_cell = item.content_paragraph_items
        rows.append([header_cell, value_cell])
    return table.Table(table.TableFormat(),
                       rows)
