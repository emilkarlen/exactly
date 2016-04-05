from xml.etree.ElementTree import Element

from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.formatting.html.paragraph_item import lists as list_rendering
from shellcheck_lib.util.textformat.formatting.html.paragraph_item import literal_layout
from shellcheck_lib.util.textformat.formatting.html.paragraph_item import paragraph
from shellcheck_lib.util.textformat.formatting.html.paragraph_item import table as table_rendering
from shellcheck_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph
from shellcheck_lib.util.textformat.structure.table import Table


class FullParagraphItemRenderer(ParagraphItemRenderer):
    def __init__(self,
                 text_renderer: text.TextRenderer):
        self.text_renderer = text_renderer

    def apply(self, parent: Element, x: ParagraphItem) -> Element:
        if isinstance(x, Paragraph):
            return self.render_paragraph(parent, x)
        if isinstance(x, lists.HeaderContentList):
            return self.render_header_value_list(parent, x)
        if isinstance(x, LiteralLayout):
            return self.render_literal_layout(parent, x)
        if isinstance(x, Table):
            return self.render_table(parent, x)
        raise TypeError('Unknown {}: {}'.format(str(ParagraphItem),
                                                str(type(x))))

    def render_literal_layout(self, parent: Element, x: LiteralLayout):
        return literal_layout.render(parent, x)

    def render_paragraph(self, parent: Element, x: Paragraph):
        return paragraph.render(self.text_renderer, parent, x)

    def render_header_value_list(self, parent: Element, x: lists.HeaderContentList):
        return list_rendering.render(self.text_renderer, self, parent, x)

    def render_table(self, parent: Element, x: Table):
        return table_rendering.render(self, parent, x)
