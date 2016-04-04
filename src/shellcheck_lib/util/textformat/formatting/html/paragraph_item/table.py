from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from shellcheck_lib.util.textformat.structure.table import Table, TableFormat


def render(paragraph_item_renderer: ParagraphItemRenderer,
           parent: Element,
           table: Table) -> Element:
    """
    :return: The added element.
    """
    rows = table.rows
    if not rows or not rows[0]:
        return parent
    t_format = table.format
    table_root = SubElement(parent, 'table')
    for row_idx, row in enumerate(rows):
        tr = SubElement(table_root, 'tr')
        for col_idx, cell in enumerate(row):
            cell_element = cell_element_for(tr, t_format, row_idx, col_idx)
            for paragraph_item in cell:
                paragraph_item_renderer.apply(cell_element, paragraph_item)
    return table_root


def cell_element_for(parent: Element, t_format: TableFormat, row_idx, col_idx) -> Element:
    if row_idx == 0 and t_format.first_row_is_header:
        return SubElement(parent, 'th')
    if col_idx == 0 and t_format.first_column_is_header:
        return SubElement(parent, 'th')
    return SubElement(parent, 'td')
