from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.formatting.html import text
from exactly_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from exactly_lib.util.textformat.formatting.html.text import Position
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.document import SectionContents, Section


class Environment:
    def __init__(self, section_level: int = 0):
        self.section_level = section_level


def increased_level(environment: Environment) -> Environment:
    return Environment(1 + environment.section_level)


class SectionHeaderRenderer:
    def apply(self,
              environment: Environment,
              parent: Element,
              header_text: core.Text) -> Element:
        raise NotImplementedError()


class HnSectionHeaderRenderer(SectionHeaderRenderer):
    def __init__(self,
                 text_renderer: text.TextRenderer):
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

    def render_section_contents(self,
                                environment: Environment,
                                parent: Element,
                                section_contents: SectionContents) -> Element:
        """
        :return: The last rendered element, or parent, if no element was rendered.
        """
        ret_val = parent
        for paragraph_item in section_contents.initial_paragraphs:
            ret_val = self.paragraph_item_renderer.apply(parent, paragraph_item)
        for section in section_contents.sections:
            ret_val = self.render_section(environment, parent, section)
        return ret_val

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
