from xml.etree.ElementTree import Element, tostring, SubElement

import shellcheck_lib.util
from shellcheck_lib.util.textformat.formatting.html.interfaces import ParagraphItemRenderer
from shellcheck_lib.util.textformat.structure import core


def as_unicode_str(root: Element):
    return tostring(root, encoding="unicode")


class CrossReferenceTarget(core.CrossReferenceTarget):
    def __init__(self, name: str):
        self.name = name


class TargetRenderer(shellcheck_lib.util.textformat.formatting.html.text.TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        assert isinstance(target, CrossReferenceTarget)
        return target.name


TARGET_RENDERER = TargetRenderer()


class ConstantPRenderer(ParagraphItemRenderer):
    def __init__(self, paragraph_contents: str):
        self.paragraph_contents = paragraph_contents

    def apply(self, parent: Element, x: core.ParagraphItem) -> Element:
        p = SubElement(parent, 'p')
        p.text = self.paragraph_contents
        return p
