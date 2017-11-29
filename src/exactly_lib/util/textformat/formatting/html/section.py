from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.formatting.html import text
from exactly_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from exactly_lib.util.textformat.formatting.html.text import Position
from exactly_lib.util.textformat.structure import core
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
              header_text: core.Text) -> Element:
        raise NotImplementedError()


class HnSectionHeaderRenderer(SectionHeaderRenderer):
    def __init__(self, text_renderer: text.TextRenderer):
        self.text_renderer = text_renderer

    def apply(self,
              environment: Environment,
              parent: Element,
              header_text: core.Text) -> Element:
        ret_val = SubElement(parent, self._resolve_header_element_tag(environment))
        self.text_renderer.apply(ret_val, ret_val, Position.INSIDE, header_text)
        return ret_val

    @staticmethod
    def _resolve_header_element_tag(environment: Environment) -> str:
        if environment.section_level <= 5:
            return 'h' + str(1 + environment.section_level)
        return 'h6'


class SectionRenderer:
    def __init__(self,
                 section_header_renderer: SectionHeaderRenderer,
                 paragraph_item_renderer: ParagraphItemRenderer):
        self.section_header_renderer = section_header_renderer
        self.paragraph_item_renderer = paragraph_item_renderer

    def render_paragraph_items(self,
                               environment: Environment,
                               parent: Element,
                               paragraph_items: list) -> Element:
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
        return _SectionItemRenderer(self, environment, parent).visit(section_item)

    def render_section(self,
                       environment: Environment,
                       parent: Element,
                       section: Section) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        last_header_element = self.section_header_renderer.apply(environment, parent, section.header)
        last_sc_elem = self.render_section_contents(increased_level(environment), parent, section.contents)
        return last_header_element if last_sc_elem is parent else last_sc_elem

    def render_article(self,
                       environment: Environment,
                       parent: Element,
                       article: Article) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        environment = root_level(environment)
        ret_val = SubElement(parent, 'article')
        self._render_article_header(environment, ret_val,
                                    article.header,
                                    article.contents.abstract_paragraphs)
        self.render_section_contents(environment, ret_val, article.contents.section_contents)
        return ret_val

    def _render_article_header(self,
                               environment: Environment,
                               parent: Element,
                               header: core.Text,
                               abstract_paragraphs: list) -> Element:
        """
        :return: The the header element
        """
        ret_val = SubElement(parent, 'header')
        self.section_header_renderer.apply(environment, ret_val, header)
        self.render_paragraph_items(environment, ret_val, abstract_paragraphs)
        return ret_val


class _SectionItemRenderer(SectionItemVisitor):
    def __init__(self,
                 renderer: SectionRenderer,
                 environment: Environment,
                 parent: Element):
        self.renderer = renderer
        self.parent = parent
        self.environment = environment

    def visit_section(self, section: Section):
        return self.renderer.render_section(self.environment, self.parent, section)

    def visit_article(self, article: Article):
        return self.renderer.render_article(self.environment, self.parent, article)
