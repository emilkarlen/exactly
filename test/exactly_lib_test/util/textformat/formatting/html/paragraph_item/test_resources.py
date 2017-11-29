from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.paragraph import Paragraph


class ConstantPRenderer(ParagraphItemRenderer):
    def __init__(self, paragraph_contents: str):
        self.paragraph_contents = paragraph_contents

    def apply(self, parent: Element, x: core.ParagraphItem,
              skip_surrounding_p_element=False) -> Element:
        if skip_surrounding_p_element:
            parent.text = self.paragraph_contents
            return parent
        else:
            p = SubElement(parent, 'p')
            p.text = self.paragraph_contents
            return p


class ParaWithSingleStrTextRenderer(ParagraphItemRenderer):
    def apply(self, parent: Element, x: core.ParagraphItem,
              skip_surrounding_p_element=False) -> Element:
        if isinstance(x, Paragraph):
            if len(x.start_on_new_line_blocks) == 1:
                text = x.start_on_new_line_blocks[0]
                if isinstance(text, core.StringText):
                    if skip_surrounding_p_element:
                        parent.text = text.value
                        return parent
                    else:
                        p = SubElement(parent, 'p')
                        p.text = text.value
                        return p
        msg = 'This test implementation of %s can only render a %s with a single %s\n. Found: %s' % (
            str(ParagraphItemRenderer),
            str(Paragraph),
            str(core.StringText),
            str(x))
        raise NotImplementedError(msg)
