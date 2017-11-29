from xml.etree.ElementTree import Element, SubElement

from exactly_lib import program_info
from exactly_lib.help.html_doc import css_classes
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import all_entity_types
from exactly_lib.util.textformat.formatting.html.utils import ElementPopulator, ComplexElementPopulator

PAGE_TITLE = 'Reference Manual for %s' % formatting.program_name(program_info.PROGRAM_NAME)
TOC_TITLE = 'Table of Contents'

_CSS_CLASSES = {
    'entity': css_classes.ENTITY,
    'concept_entity': all_entity_types.CONCEPT_ENTITY_TYPE_NAMES,
}

ELEMENT_STYLES_ = """\
pre {{
  background-color : #EEFFCC;
  padding: 7px;
  border: 1px solid #cEdFaC;
}}

h1 {{
  background-color: #80bfff;
  padding: 5px;
}}

article h1 {{
    font-size: large;
    padding: 0px;
    background-color: transparent;
}}

article h2 {{
    font-size: medium;
}}

article h3 {{
    font-size: medium;
}}

article header h1 {{
    padding: 7px;
    font-size: x-large;
    font-family: monospace;
    background-color: #c0c0c0;
}}

article.{entity}.{concept_entity} header h1 {{
    font-family: inherit;
}}

article header p {{
    font-style: italic;
    font-size: 110%;
}}

table {{
  border-collapse: collapse;
}}

th {{
  font-weight: normal;
  background-color: #f4f4f4;
  text-align: left;
  padding-right: 5px;
  vertical-align: top;
}}

td {{
  vertical-align: top;
}}

a:link {{
  text-decoration: none;
}}


a:hover {{
  text-decoration: underline;
}}

"""

ELEMENT_STYLES = ELEMENT_STYLES_.format_map(_CSS_CLASSES)

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
        version.text = formatting.program_name(program_info.PROGRAM_NAME) + ' version ' + program_info.VERSION
        SubElement(parent, 'hr')


HEADER_POPULATOR = ComplexElementPopulator([
    DivWithTextAndStylePopulator(PAGE_TITLE, TITLE_STYLE),
    VersionPopulator(),
    DivWithTextAndStylePopulator(TOC_TITLE, TOC_TITLE_STYLE),
])
