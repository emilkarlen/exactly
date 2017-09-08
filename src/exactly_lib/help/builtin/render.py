import functools

from exactly_lib.help.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.help.utils.rendering import parttioned_entity_set as pes
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.utils.rendering.parttioned_entity_set import PartitionNamesSetup
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def _builtin_docs_of_value_type(value_type: ValueType, builtin_doc_list: list) -> list:
    return list(filter(lambda builtin_doc: builtin_doc.value_type is value_type,
                       builtin_doc_list))


# _PARTITIONS_SETUP_tmpl = [
#     pes.PartitionSetup(pes.PartitionNamesSetup('data-type',
#                                                'Data types'),
#                        functools.partial(_type_docs_of_type_category, ElementType.SYMBOL)
#                        ),
#     pes.PartitionSetup(pes.PartitionNamesSetup('logic-type',
#                                                'Logic types'),
#                        functools.partial(_type_docs_of_type_category, ElementType.LOGIC)
#                        ),
# ]
# TODO Sortering av typerna
_PARTITIONS_SETUP = [
    pes.PartitionSetup(PartitionNamesSetup(
        str(value_type).lower(),
        str(value_type),  # TODO
    ),
        functools.partial(_builtin_docs_of_value_type, value_type))
    for value_type in ValueType
]


class IndividualBuiltinSymbolRenderer(SectionContentsRenderer):
    def __init__(self, builtin_doc: BuiltinSymbolDocumentation):
        self.builtin_doc = builtin_doc
        format_map = {
            # 'type_concept': formatting.concept(TYPE_CONCEPT_INFO.name().singular),
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        initial_paragraphs = [docs.para(self.builtin_doc.single_line_description())]
        initial_paragraphs.extend(self.builtin_doc.description.initial_paragraphs)
        return doc.SectionContents(initial_paragraphs, self.builtin_doc.description.sections)


def hierarchy_generator_getter() -> pes.HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(_PARTITIONS_SETUP,
                                                   IndividualBuiltinSymbolRenderer)


def list_renderer_getter() -> pes.CliListRendererGetter:
    return pes.PartitionedCliListRendererGetter(
        _PARTITIONS_SETUP,
        single_line_description_as_summary_paragraphs)
