from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import type_system, formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts, types
from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.entities.types import all_types
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.lists import ListType, HeaderContentListItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _TypeConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.TYPE_CONCEPT_INFO)
        self._parser = TextParser({
            'type': concepts.TYPE_CONCEPT_INFO.name,

            'program_name': formatting.program_name(program_info.PROGRAM_NAME),

            'string_type': types.STRING_TYPE_INFO.name,
            'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = self._parser.fnap(_REST__BEFORE_CATEGORY_LIST)
        rest_paragraphs.append(_types_categories_list(self._parser))
        rest_paragraphs += (self._parser.fnap(_REST__AFTER_CATEGORY_LIST))
        sub_sections = [
            docs.section(
                self._parser.text('Summary of {type:s}'),
                [_types_list()]
            )
        ]
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs,
                                                          sub_sections))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return list(map(lambda type_doc: type_doc.cross_reference_target(),
                        all_types.all_types()))


TYPE_CONCEPT = _TypeConcept()

_REST__BEFORE_CATEGORY_LIST = """\
{program_name} has a type system specialized for test cases.


Every symbol, and most {instruction} arguments, have a {type}.


There are two categories of {type:s}:
"""

_REST__AFTER_CATEGORY_LIST = """\
Each {type} has its own specialized syntax. 
"""

_TYPE_CATEGORY__DATA = """\
These {type:s} represent pure data, and can be converted to {string_type:s}.
"""

_TYPE_CATEGORY__LOGIC = """\
These {type:s} involve data together with logic that is executed. 


Most of these {type:s} have syntax that resembles common syntax of expressions,
with primitives and operators.
"""

_TYPE_CATEGORY_DESCRIPTION = {
    TypeCategory.DATA: _TYPE_CATEGORY__DATA,
    TypeCategory.LOGIC: _TYPE_CATEGORY__LOGIC,
}


def _types_categories_list(tp: TextParser) -> ParagraphItem:
    return docs.simple_list_with_space_between_elements_and_content([
        docs.list_item(
            type_system.TYPE_CATEGORY_NAME[category],
            tp.fnap(_TYPE_CATEGORY_DESCRIPTION[category])
        )
        for category in type_system.TypeCategory
    ],
        ListType.ITEMIZED_LIST,
    )


def _types_list() -> ParagraphItem:
    return docs.simple_list_with_space_between_elements_and_content([
        _types_category_list_item(category)
        for category in type_system.TypeCategory
    ],
        ListType.ITEMIZED_LIST,
    )


def _types_category_list_item(category: TypeCategory) -> HeaderContentListItem:
    return docs.list_item(
        type_system.TYPE_CATEGORY_NAME[category],
        [_list_types_in_category(category)]
    )


def _list_types_in_category(type_category: TypeCategory) -> ParagraphItem:
    from exactly_lib.help.entities.types.contents_structure import TypeDocumentation

    def row(type_doc: TypeDocumentation) -> List[docs.TableCell]:
        return [
            docs.text_cell(type_doc.singular_name_text),
            docs.text_cell(type_doc.single_line_description()),
        ]

    type_docs = all_types.type_docs_of_type_category(type_category, all_types.all_types())
    rows = list(map(row,
                    sorted(type_docs,
                           key=lambda type_doc: type_doc.name().singular)))
    return docs.first_column_is_header_table(rows, docs.COLON_TABLE_COLUMN_SEPARATOR)
