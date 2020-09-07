from typing import Sequence, Dict
from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.rendering.html import text
from exactly_lib.util.textformat.rendering.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.rendering.html.paragraph_item.interfaces import ParagraphItemRenderer
from exactly_lib.util.textformat.rendering.html.text import Position
from exactly_lib.util.textformat.rendering.html.utils import set_class_attribute
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents, Section, SectionItemVisitor, SectionItem, \
    Article


class Environment:
    def __init__(self, section_level: int = 0):
        self.section_level = section_level


def increased_level(environment: Environment) -> Environment:
    return Environment(1 + environment.section_level)


def root_level(environment: Environment) -> Environment:
    return Environment(0)


class SectionHeaderRenderer:
    def apply(self,
              environment: Environment,
              parent: Element,
              header_text: core.Text,
              header_element_attributes: dict) -> Element:
        raise NotImplementedError()


class HnSectionHeaderRenderer(SectionHeaderRenderer):
    def __init__(self, text_renderer: text.TextRenderer):
        self.text_renderer = text_renderer

    def apply(self,
              environment: Environment,
              parent: Element,
              header_text: core.Text,
              header_element_attributes: dict) -> Element:
        ret_val = SubElement(parent, self._resolve_header_element_tag(environment),
                             header_element_attributes)
        self.text_renderer.apply(ret_val, ret_val, Position.INSIDE, header_text)
        return ret_val

    @staticmethod
    def _resolve_header_element_tag(environment: Environment) -> str:
        if environment.section_level <= 5:
            return 'h' + str(1 + environment.section_level)
        return 'h6'


class SectionItemRenderer:
    def __init__(self,
                 target_renderer: TargetRenderer,
                 section_header_renderer: SectionHeaderRenderer,
                 paragraph_item_renderer: ParagraphItemRenderer):
        self.target_renderer = target_renderer
        self.section_header_renderer = section_header_renderer
        self.paragraph_item_renderer = paragraph_item_renderer

    def render_paragraph_items(self,
                               environment: Environment,
                               parent: Element,
                               paragraph_items: Sequence[ParagraphItem]) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        ret_val = parent
        for paragraph_item in paragraph_items:
            ret_val = self.paragraph_item_renderer.apply(parent, paragraph_item)
        return ret_val

    def render_section_contents(self,
                                environment: Environment,
                                parent: Element,
                                section_contents: SectionContents) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        ret_val = self.render_paragraph_items(environment, parent, section_contents.initial_paragraphs)
        for section in section_contents.sections:
            ret_val = self.render_section_item(environment, parent, section)
        return ret_val

    def render_section_item(self,
                            environment: Environment,
                            parent: Element,
                            section_item: SectionItem) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        return section_item.accept(_SectionItemRenderer(self, environment, parent))

    def render_section(self,
                       environment: Environment,
                       parent: Element,
                       section: Section) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        ret_val = SubElement(parent, 'section', self._root_element_attributes(section))
        self._render_header(environment, ret_val,
                            section.header,
                            [])
        self.render_section_contents(increased_level(environment), ret_val, section.contents)
        return ret_val

    def render_article(self,
                       environment: Environment,
                       parent: Element,
                       article: Article) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        environment = root_level(environment)

        ret_val = SubElement(parent, 'article', self._root_element_attributes(article))
        self._render_header(environment, ret_val,
                            article.header,
                            article.contents.abstract_paragraphs)
        self.render_section_contents(environment, ret_val, article.contents.section_contents)
        return ret_val

    def _render_header(self,
                       environment: Environment,
                       parent: Element,
                       header: core.Text,
                       paragraphs: Sequence[ParagraphItem]) -> Element:
        """
        :return: The the header element
        """
        ret_val = SubElement(parent, 'header')
        self.section_header_renderer.apply(environment, ret_val, header, {})
        self.render_paragraph_items(environment, ret_val, paragraphs)
        return ret_val

    def _root_element_attributes(self, section_item: SectionItem) -> Dict[str, str]:
        ret_val = {}

        if section_item.target:
            id_value = self.target_renderer.apply(section_item.target)
            ret_val['id'] = id_value
        set_class_attribute(ret_val, section_item)
        return ret_val


class _SectionItemRenderer(SectionItemVisitor[Element]):
    def __init__(self,
                 renderer: SectionItemRenderer,
                 environment: Environment,
                 parent: Element):
        self.renderer = renderer
        self.parent = parent
        self.environment = environment

    def visit_section(self, section: Section) -> Element:
        return self.renderer.render_section(self.environment, self.parent, section)

    def visit_article(self, article: Article) -> Element:
        return self.renderer.render_article(self.environment, self.parent, article)
