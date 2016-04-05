from xml.etree.ElementTree import Element

from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.formatting.html.paragraph_item.interfaces import ParagraphItemRenderer
from shellcheck_lib.util.textformat.structure.document import SectionContents, Section


class Environment:
    def __init__(self, section_level: int = 0):
        self.section_level = section_level


class SectionRenderer:
    def __init__(self,
                 text_renderer: text.TextRenderer,
                 paragraph_item_renderer: ParagraphItemRenderer):
        self.text_renderer = text_renderer
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
        return ret_val

    def render_section(self, environment: Environment, parent: Element, section: Section):
        raise NotImplementedError()
