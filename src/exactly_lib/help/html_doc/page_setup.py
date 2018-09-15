from xml.etree.ElementTree import Element, SubElement

from exactly_lib import program_info
from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import all_entity_types
from exactly_lib.help import std_tags
from exactly_lib.util.textformat.rendering.html.utils import ElementPopulator, ComplexElementPopulator

PAGE_TITLE = 'Reference Manual for %s' % formatting.program_name(program_info.PROGRAM_NAME)
TOC_TITLE = 'Table of Contents'

_CSS_CLASSES = {
    'toc': std_tags.TOC_SECTION,
    'entity': std_tags.ENTITY,
    'section': std_tags.SECTION,
    'syntax_text': std_tags.SYNTAX_TEXT,
    'enum_constant': std_tags.ENUM_CONSTANT,
    'text_as_header': std_tags.TEXT_AS_HEADER,
    'actor_entity': all_entity_types.ACTOR_ENTITY_TYPE_NAMES.identifier,
    'concept_entity': all_entity_types.CONCEPT_ENTITY_TYPE_NAMES.identifier,
    'type_entity': all_entity_types.TYPE_ENTITY_TYPE_NAMES.identifier,
}

ELEMENT_STYLES_ = """\
pre {{
  background-color : #EEFFCC;
  padding: 7px;
  border: 1px solid #cEdFaC;
}}

.{syntax_text} {{
  font-family: monospace;
}}


.{enum_constant} {{
  font-weight: bold;
}}


.{text_as_header} {{
  font-weight: bold;
}}


section.{toc} > header > h1 {{
  padding: 5px;
  border-bottom: thick solid black;
}}

section.{toc} > header > h2 {{
  padding: 2px;
  border-bottom: medium solid black;
}}

section.{toc} > header > h3 {{
  padding: 2px;
  border-bottom: thin solid black;
}}


article > header > h1 {{
  padding: 3px;
  font-size: x-large;
  background-color: #c0c0c0;
}}

article > header > p {{
  font-style: italic;
  font-size: 110%;
}}

article section > header > h1 {{
    font-size: large;
}}

article section > header > h2 {{
    font-size: medium;
}}

article.{section} > header > h1 {{
  font-size: xx-large;
  background-color: LightGoldenRodYellow;
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
