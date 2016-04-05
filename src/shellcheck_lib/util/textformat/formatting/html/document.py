from xml.etree.ElementTree import Element, SubElement, ElementTree

from shellcheck_lib.util.textformat.formatting.html.section import SectionRenderer, Environment
from shellcheck_lib.util.textformat.structure.document import SectionContents


class DocumentSetup:
    def __init__(self, page_title: str):
        self.page_title = page_title


class DocumentRenderer:
    """
    Renders a XHTML 1.0 document.
    """

    def __init__(self,
                 section_renderer: SectionRenderer):
        self.section_renderer = section_renderer

    def apply(self,
              output_file,
              document_setup: DocumentSetup,
              section_contents: SectionContents):
        html = self._element_tree(document_setup, section_contents)
        output_file.write(DOCTYPE_XHTML1_0)
        ElementTree(html).write(output_file, encoding="unicode")

    def _element_tree(self,
                      document_setup: DocumentSetup,
                      section_contents: SectionContents) -> Element:
        html = Element('html')
        html.append(self._head_element(document_setup))
        body = SubElement(html, 'body')
        self.section_renderer.render_section_contents(Environment(0),
                                                      body,
                                                      section_contents)
        return html

    def _head_element(self, document_setup: DocumentSetup) -> Element:
        ret_val = Element('head')
        title = SubElement(ret_val, 'title')
        title.text = document_setup.page_title
        return ret_val


DOCTYPE_XHTML1_0 = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ' \
                   '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
