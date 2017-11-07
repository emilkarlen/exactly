from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.entities.types import all_types
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.names import formatting
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.lists import ListType


class _TypeConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.TYPE_CONCEPT_INFO)
        self._parser = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'data': 'data',
            'logic': 'logic',
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = self._parser.fnap(_REST_DESCRIPTION_1)
        rest_paragraphs += [
            _categories_list(self._list_header('{data} types'),
                             self._list_header('{logic} types'))
        ]
        rest_paragraphs += self._parser.fnap(_REST_DESCRIPTION_2)
        sub_sections = []
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs,
                                                          sub_sections))

    def _list_header(self, template_string: str) -> str:
        return self._parser.format(template_string).capitalize()


TYPE_CONCEPT = _TypeConcept()

_REST_DESCRIPTION_1 = """\
{program_name} has a type system specialized for test cases.


Every symbol, and most instruction arguments, have a type.


There are two categories of types
"""

_REST_DESCRIPTION_2 = """\
A {data} type values is pure data.


A {logic} type values is a pure function.


The {logic} types all have a syntax that resembles common syntax of expressions.

Each {data} type, on the other hand, has it's own specialized syntax. 
"""


def _categories_list(data_types_header: str, logic_types_header: str) -> ParagraphItem:
    items = [
        docs.list_item(data_types_header,
                       [_list_types_in_category(TypeCategory.DATA)]),
        docs.list_item(logic_types_header,
                       [_list_types_in_category(TypeCategory.LOGIC)]),
    ]
    return docs.simple_list(items, ListType.ITEMIZED_LIST)


def _list_types_in_category(type_category: TypeCategory) -> ParagraphItem:
    type_docs = all_types.type_docs_of_type_category(type_category, all_types.all_types())
    items = list(map(lambda type_name: docs.header_only_item(type_name),
                     sorted(map(lambda type_doc: type_doc.name().singular,
                                type_docs))))
    return docs.simple_list(items, ListType.VARIABLE_LIST)
