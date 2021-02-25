import functools
from typing import List

from exactly_lib.definitions.entity import types, concepts
from exactly_lib.definitions.entity.all_entity_types import BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.help.contents_structure.entity import HtmlDocHierarchyGeneratorGetter, CliListConstructorGetter
from exactly_lib.help.entities.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.help.render import partitioned_entity_set as pes
from exactly_lib.help.render.doc_utils import description_section_if_non_empty
from exactly_lib.help.render.entity_docs import \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def _builtin_docs_of_value_type(value_type: ValueType,
                                builtin_doc_list: List[BuiltinSymbolDocumentation]) -> List[BuiltinSymbolDocumentation]:
    return list(filter(lambda builtin_doc: builtin_doc.value_type is value_type,
                       builtin_doc_list))


# FIXME Sort on types
def _header(value_type: ValueType) -> str:
    return '{type_name} {symbols}'.format(
        type_name=types.VALUE_TYPE_2_TYPES_INFO_DICT[value_type].name.singular.capitalize(),
        symbols=SYMBOL_CONCEPT_INFO.name.plural)


_PARTITIONS_SETUP = [
    pes.PartitionSetup(
        pes.PartitionNamesSetup(
            str(value_type).lower(),
            _header(value_type),
        ),
        functools.partial(_builtin_docs_of_value_type, value_type)
    )
    for value_type in ValueType
]


class IndividualBuiltinSymbolConstructor(ArticleContentsConstructor):
    def __init__(self, builtin_doc: BuiltinSymbolDocumentation):
        self.builtin_doc = builtin_doc

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        initial_paragraphs = [
            self._type_paragraph(),
        ]
        sub_sections = description_section_if_non_empty(self.builtin_doc.description)
        sub_sections += self._see_also_sections(environment)
        return doc.ArticleContents(docs.paras(self.builtin_doc.single_line_description()),
                                   doc.SectionContents(initial_paragraphs,
                                                       sub_sections))

    def _type_paragraph(self) -> docs.ParagraphItem:
        type_name = types.VALUE_TYPE_2_TYPES_INFO_DICT[self.builtin_doc.value_type].name.singular
        return docs.para(': '.join((concepts.TYPE_CONCEPT_INFO.singular_name.capitalize(),
                                    type_name)))

    def _see_also_sections(self, environment: ConstructionEnvironment) -> List[doc.SectionItem]:
        type_info = types.VALUE_TYPE_2_TYPES_INFO_DICT[self.builtin_doc.value_type]
        targets = [type_info.cross_reference_target] + list(self.builtin_doc.see_also)
        return see_also_sections(targets,
                                 environment)


def hierarchy_generator_getter() -> HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.identifier,
                                                   _PARTITIONS_SETUP,
                                                   IndividualBuiltinSymbolConstructor)


def list_renderer_getter() -> CliListConstructorGetter:
    return pes.PartitionedCliListConstructorGetter(
        _PARTITIONS_SETUP,
        single_line_description_as_summary_paragraphs)
