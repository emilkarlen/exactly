from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import lists, table
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.structures import simple_header_only_list


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
