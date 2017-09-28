import functools

from exactly_lib.help.entities.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.help.utils.doc_utils import description_section_if_non_empty
from exactly_lib.help.utils.rendering import parttioned_entity_set as pes
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.utils.rendering.parttioned_entity_set import PartitionNamesSetup
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.help_texts.type_system import TYPE_INFO_DICT
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def _builtin_docs_of_value_type(value_type: ValueType, builtin_doc_list: list) -> list:
    return list(filter(lambda builtin_doc: builtin_doc.value_type is value_type,
                       builtin_doc_list))


# TODO Sortering av typerna
def _header(value_type: ValueType) -> str:
    return '{type_name} {symbols}'.format(
        type_name=TYPE_INFO_DICT[value_type].concept_info.name.singular.capitalize(),
        symbols=SYMBOL_CONCEPT_INFO.name.plural)


_PARTITIONS_SETUP = [
    pes.PartitionSetup(PartitionNamesSetup(
        str(value_type).lower(),
        _header(value_type),
    ),
        functools.partial(_builtin_docs_of_value_type, value_type))
    for value_type in ValueType
]


class IndividualBuiltinSymbolRenderer(SectionContentsRenderer):
    def __init__(self, builtin_doc: BuiltinSymbolDocumentation):
        self.builtin_doc = builtin_doc

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        initial_paragraphs = [
            docs.para(self.builtin_doc.single_line_description()),
            self._type_paragraph(),
        ]
        sub_sections = description_section_if_non_empty(self.builtin_doc.description)
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _type_paragraph(self) -> docs.ParagraphItem:
        return docs.para('Type: ' + TYPE_INFO_DICT[self.builtin_doc.value_type].concept_info.name.singular)


def hierarchy_generator_getter() -> pes.HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(_PARTITIONS_SETUP,
                                                   IndividualBuiltinSymbolRenderer)


def list_renderer_getter() -> pes.CliListRendererGetter:
    return pes.PartitionedCliListRendererGetter(
        _PARTITIONS_SETUP,
        single_line_description_as_summary_paragraphs)
