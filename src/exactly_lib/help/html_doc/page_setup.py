from xml.etree.ElementTree import Element, SubElement

from exactly_lib import program_info
from exactly_lib.util.textformat.formatting.html.utils import ElementPopulator, ComplexElementPopulator

PAGE_TITLE = '%s Reference Manual' % program_info.PROGRAM_NAME
TOC_TITLE = 'Table of Contents'
ELEMENT_STYLES = """\
pre {
background-color : #EEFFCC;
padding: 7px;
border: 1px solid #cEdFaC;
border-radius     : 3px;
}

h1 {
background-color: #E6E6FA;
border-radius     : 4px;
padding: 5px;
}

"""
TITLE_STYLE = """\
font-size: 250%;
font-weight: bold;
"""
TOC_TITLE_STYLE = """\
font-size: 200%;
font-weight: bold;
"""


class StylePopulator(ElementPopulator):
    def __init__(self, style: str):
        self.style = style

    def apply(self, parent: Element):
        SubElement(parent, 'style').text = self.style


class DivWithTextAndStylePopulator(ElementPopulator):
    def __init__(self,
                 contents: str,
                 style: str):
        self.contents = contents
        self.style = style

    def apply(self, parent: Element):
        div = SubElement(parent, 'div')
        div.text = self.contents
        div.set('style', self.style)


class VersionPopulator(ElementPopulator):
    def apply(self, parent: Element):
        version = SubElement(parent, 'p')
        version.text = program_info.PROGRAM_NAME + ' version ' + program_info.VERSION
        SubElement(parent, 'hr')


HEADER_POPULATOR = ComplexElementPopulator([
    DivWithTextAndStylePopulator(PAGE_TITLE, TITLE_STYLE),
    VersionPopulator(),
    DivWithTextAndStylePopulator(TOC_TITLE, TOC_TITLE_STYLE),
])