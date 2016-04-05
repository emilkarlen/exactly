from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from shellcheck_lib.util.textformat.formatting.html.text import TargetRenderer
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph


class CrossReferenceTarget(core.CrossReferenceTarget):
    def __init__(self, name: str):
        self.name = name


class TargetRendererTestImpl(TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        assert isinstance(target, CrossReferenceTarget)
        return target.name


class ConstantPRenderer(ParagraphItemRenderer):
    def __init__(self, paragraph_contents: str):
        self.paragraph_contents = paragraph_contents

    def apply(self, parent: Element, x: core.ParagraphItem) -> Element:
        p = SubElement(parent, 'p')
        p.text = self.paragraph_contents
        return p


class ParaWithSingleStrTextRenderer(ParagraphItemRenderer):
    def apply(self, parent: Element, x: core.ParagraphItem) -> Element:
        if isinstance(x, Paragraph):
            if len(x.start_on_new_line_blocks) == 1:
                text = x.start_on_new_line_blocks[0]
                if isinstance(text, core.StringText):
                    p = SubElement(parent, 'p')
                    p.text = text.value
                    return p
        msg = 'This test implementation of %s can only render a %s with a single %s\n. Found: %s' % (
            str(ParagraphItemRenderer),
            str(Paragraph),
            str(core.StringText),
            str(x))
        raise NotImplementedError(msg)
