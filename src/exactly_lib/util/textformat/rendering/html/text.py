import enum
from typing import Callable
from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.rendering.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.rendering.html.utils import set_class_attribute_on_element
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import Text


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
        return text.accept(setter)


class ContentSetter(core.TextVisitor[Element]):
    def __init__(self,
                 target_renderer: TargetRenderer,
                 content_root: Element,
                 str_setter: Callable[[str], None]):
        self.target_renderer = target_renderer
        self.content_root = content_root
        self.str_setter = str_setter

    def visit_string(self, text: core.StringText) -> Element:
        if text.tags:
            a = SubElement(self.content_root, 'span')
            a.text = text.value
            set_class_attribute_on_element(a, text)
            return a
        else:
            self.str_setter(text.value)
            return self.content_root

    def visit_cross_reference(self, text: core.CrossReferenceText) -> Element:
        a = SubElement(self.content_root, 'a')
        target_str = self._target_str(text)
        a.set('href', target_str)
        set_class_attribute_on_element(a, text)
        content_setter = ContentSetter(self.target_renderer,
                                       a,
                                       set_text_inside(a))
        text.title_text.accept(content_setter)
        return a

    def visit_anchor(self, text: core.AnchorText) -> Element:
        a = SubElement(self.content_root, 'span')
        a.set('id', self.target_renderer.apply(text.anchor))
        content_setter = ContentSetter(self.target_renderer,
                                       a,
                                       set_text_inside(a))
        text.anchored_text.accept(content_setter)
        return a

    def _target_str(self, text: core.CrossReferenceText) -> str:
        ret_val = self.target_renderer.apply(text.target)
        if text.target_is_id_in_same_document:
            ret_val = '#' + ret_val
        return ret_val


def set_text_inside(e: Element):
    def ret_val(s: str):
        e.text = s

    return ret_val


def set_text_after(e: Element):
    def ret_val(s: str):
        e.tail = s

    return ret_val
