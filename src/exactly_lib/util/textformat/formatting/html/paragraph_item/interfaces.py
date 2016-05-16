from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.structure.core import ParagraphItem


class ParagraphItemRenderer:
    def apply(self, parent: Element, x: ParagraphItem,
              skip_surrounding_p_element=False) -> Element:
        raise NotImplementedError()
