from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import type_system, formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.entities.types import all_types
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.lists import ListType
from exactly_lib.util.textformat.textformat_parser import TextParser


class _TypeConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.TYPE_CONCEPT_INFO)
        self._parser = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'data': type_system.DATA_TYPE_CATEGORY_NAME,
            'logic': type_system.LOGIC_TYPE_CATEGORY_NAME,
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

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return list(map(lambda type_doc: type_doc.cross_reference_target(),
                        all_types.all_types()))


TYPE_CONCEPT = _TypeConcept()

_REST_DESCRIPTION_1 = """\
{program_name} has a type system specialized for test cases.


Every symbol, and most instruction arguments, have a type.


There are two categories of types
"""

_REST_DESCRIPTION_2 = """\
A {data} type values is pure data.


A {logic} type values is a pure function.


Each {data} type has it's own specialized syntax. 

The {logic} types have syntax that resembles common syntax of expressions.
"""


def _categories_list(data_types_header: str, logic_types_header: str) -> ParagraphItem:
    items = [
        docs.list_item(data_types_header,
                       [_list_types_in_category(TypeCategory.DATA)]),
        docs.list_item(logic_types_header,
                       [_list_types_in_category(TypeCategory.LOGIC)]),
    ]
    return docs.simple_list_with_space_between_elements_and_content(items, ListType.ITEMIZED_LIST)


def _list_types_in_category(type_category: TypeCategory) -> ParagraphItem:
    from exactly_lib.help.entities.types.contents_structure import TypeDocumentation

    def row(type_doc: TypeDocumentation) -> List[docs.TableCell]:
        return [
            docs.text_cell(type_doc.name().singular),
            docs.text_cell(type_doc.single_line_description()),
        ]

    type_docs = all_types.type_docs_of_type_category(type_category, all_types.all_types())
    rows = list(map(row,
                    sorted(type_docs,
                           key=lambda type_doc: type_doc.name().singular)))
    return docs.first_column_is_header_table(rows, docs.COLON_TABLE_COLUMN_SEPARATOR)
