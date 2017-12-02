from xml.etree.ElementTree import Element, SubElement, tostring

from exactly_lib.util.textformat.rendering.html.section import SectionItemRenderer, Environment
from exactly_lib.util.textformat.rendering.html.utils import ElementPopulator
from exactly_lib.util.textformat.structure.document import SectionContents


class DocumentSetup:
    def __init__(self,
                 page_title: str,
                 head_populator: ElementPopulator = ElementPopulator(),
                 header_populator: ElementPopulator = ElementPopulator(),
                 footer_populator: ElementPopulator = ElementPopulator()):
        self.page_title = page_title
        self.head_populator = head_populator
        self.header_populator = header_populator
        self.footer_populator = footer_populator


class DocumentRenderer:
    """
    Renders a XHTML 1.0 document.
    """

    def __init__(self,
                 section_renderer: SectionItemRenderer):
        self.section_renderer = section_renderer

    def apply(self,
              output_file,
              document_setup: DocumentSetup,
              section_contents: SectionContents):
        html = self._element_tree(document_setup, section_contents)
        s = tostring(html,
                     method='html',
                     encoding='unicode')
        output_file.write(DOCTYPE_XHTML1_0)
        output_file.write(s)

    def _element_tree(self,
                      document_setup: DocumentSetup,
                      section_contents: SectionContents) -> Element:
        html = Element('html')
        html.append(self._head_element(document_setup))
        body = SubElement(html, 'body')
        document_setup.header_populator.apply(body)
        self.section_renderer.render_section_contents(Environment(0),
                                                      body,
                                                      section_contents)
        document_setup.footer_populator.apply(body)
        return html

    def _head_element(self, document_setup: DocumentSetup) -> Element:
        ret_val = Element('head')
        title = SubElement(ret_val, 'title')
        title.text = document_setup.page_title
        document_setup.head_populator.apply(ret_val)
        return ret_val


DOCTYPE_XHTML1_0 = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ' \
                   '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
