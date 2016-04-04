import types
from functools import partial
from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph


class TargetRenderer:
    """
    Abstract base class for rendering of a cross reference target.
    """

    def apply(self, target: core.CrossReferenceTarget) -> str:
        raise NotImplementedError()


def render(target_renderer: TargetRenderer,
           parent: Element,
           paragraph: Paragraph) -> Element:
    """
    :param para:
    :return: parent, if the paragraph is empty. Otherwise the added p element.
    """
    start_on_new_line_blocks = paragraph.start_on_new_line_blocks
    if not start_on_new_line_blocks:
        return parent
    p = SubElement(parent, 'p')

    content_setter = _ContentSetter(target_renderer,
                                    p,
                                    partial(_set_text, p))

    content_setter.visit(start_on_new_line_blocks[0])
    for text in start_on_new_line_blocks[1:]:
        br = SubElement(p, 'br')
        content_setter.str_setter = partial(_set_tail, br)
        content_setter.visit(text)
    return p


class _ContentSetter(core.TextVisitor):
    def __init__(self,
                 target_renderer: TargetRenderer,
                 content_root: Element,
                 str_setter: types.FunctionType):
        self.target_renderer = target_renderer
        self.content_root = content_root
        self.str_setter = str_setter

    def visit_string(self, text: core.StringText):
        self.str_setter(text.value)

    def visit_cross_reference(self, text: core.CrossReferenceText):
        a = SubElement(self.content_root, 'a')
        a.set('href', self.target_renderer.apply(text.target))
        a.text = text.title

    def visit_anchor(self, text: core.AnchorText):
        a = SubElement(self.content_root, 'a')
        a.set('name', self.target_renderer.apply(text.anchor))
        anchor_content_setter = _ContentSetter(self.target_renderer,
                                               a,
                                               partial(_set_text, a))
        anchor_content_setter.visit(text.anchored_text)


def _set_text(e: Element, s: str):
    e.text = s


def _set_tail(e: Element, s: str):
    e.tail = s
