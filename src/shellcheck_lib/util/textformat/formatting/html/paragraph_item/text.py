import enum
import types
from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.core import Text


class TargetRenderer:
    """
    Abstract base class for rendering of a cross reference target.
    """

    def apply(self, target: core.CrossReferenceTarget) -> str:
        raise NotImplementedError()


class Position(enum.Enum):
    INSIDE = 1
    AFTER = 2


class TextRenderer:
    def __init__(self,
                 target_renderer: TargetRenderer):
        self.target_renderer = target_renderer

    def apply(self, element_container: Element, text_container: Element, position: Position, text: Text) -> Element:
        if position is Position.INSIDE:
            str_setter = set_text_inside(text_container)
        else:
            str_setter = set_text_after(text_container)

        setter = ContentSetter(self.target_renderer, element_container, str_setter)
        return setter.visit(text)


class ContentSetter(core.TextVisitor):
    def __init__(self,
                 target_renderer: TargetRenderer,
                 content_root: Element,
                 str_setter: types.FunctionType):
        self.target_renderer = target_renderer
        self.content_root = content_root
        self.str_setter = str_setter

    def visit_string(self, text: core.StringText):
        self.str_setter(text.value)
        return self.content_root

    def visit_cross_reference(self, text: core.CrossReferenceText):
        a = SubElement(self.content_root, 'a')
        a.set('href', self.target_renderer.apply(text.target))
        a.text = text.title
        return a

    def visit_anchor(self, text: core.AnchorText):
        a = SubElement(self.content_root, 'a')
        a.set('name', self.target_renderer.apply(text.anchor))
        anchor_content_setter = ContentSetter(self.target_renderer,
                                              a,
                                              set_text_inside(a))
        return anchor_content_setter.visit(text.anchored_text)


def set_text_inside(e: Element):
    def ret_val(s: str):
        e.text = s

    return ret_val


def set_text_after(e: Element):
    def ret_val(s: str):
        e.tail = s

    return ret_val
