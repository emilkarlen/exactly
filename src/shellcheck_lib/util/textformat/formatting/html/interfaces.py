from xml.etree.ElementTree import Element

from shellcheck_lib.util.textformat.structure.core import ParagraphItem


class AnyParagraphItemRenderer:
    def apply(self, parent: Element, x: ParagraphItem) -> Element:
        raise NotImplementedError()
