import functools

from exactly_lib.definitions import type_system
from exactly_lib.definitions.entity.all_entity_types import TYPE_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.contents_structure.entity import HtmlDocHierarchyGeneratorGetter, CliListConstructorGetter
from exactly_lib.help.entities.types import all_types
from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render import partitioned_entity_set as pes
from exactly_lib.help.render.doc_utils import synopsis_section
from exactly_lib.help.render.entity_docs import \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser
from exactly_lib.util.textformat.utils import append_section_if_contents_is_non_empty

LOGIC_TYPES_HEADER = type_system.LOGIC_TYPE_CATEGORY_NAME.capitalize() + ' types'

DATA_TYPES_HEADER = type_system.DATA_TYPE_CATEGORY_NAME.capitalize() + ' types'

_PARTITIONS_SETUP = [
    pes.PartitionSetup(pes.PartitionNamesSetup('data-type',
                                               DATA_TYPES_HEADER),
                       functools.partial(all_types.type_docs_of_type_category, TypeCategory.DATA)
                       ),
    pes.PartitionSetup(pes.PartitionNamesSetup('logic-type',
                                               LOGIC_TYPES_HEADER),
                       functools.partial(all_types.type_docs_of_type_category, TypeCategory.LOGIC)
                       ),
]


class IndividualTypeConstructor(ArticleContentsConstructor):
    def __init__(self, type_doc: TypeDocumentation):
        self.doc = type_doc
        format_map = {
            'act_phase': phase_names.ACT.emphasis,
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        sub_sections = []

        if self.doc.invokation_variants():
            sub_sections.append(synopsis_section(
                invokation_variants_content(None,
                                            self.doc.invokation_variants(),
                                            self.doc.syntax_elements())))
        append_section_if_contents_is_non_empty(sub_sections,
                                                'Description',
                                                self.doc.main_description_rest())
        sub_sections += see_also_sections(self.doc.see_also_targets(),
                                          environment,
                                          uppercase_title=True)
        return doc.ArticleContents(docs.paras(self.doc.single_line_description()),
                                   doc.SectionContents([],
                                                       sub_sections))


def hierarchy_generator_getter() -> HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(TYPE_ENTITY_TYPE_NAMES.identifier,
                                                   _PARTITIONS_SETUP,
                                                   IndividualTypeConstructor)


def list_render_getter() -> CliListConstructorGetter:
    return pes.PartitionedCliListConstructorGetter(
        _PARTITIONS_SETUP,
        single_line_description_as_summary_paragraphs)
