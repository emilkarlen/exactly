from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.types.contents_structure import TypeDocumentation
from exactly_lib.help.utils.doc_utils import synopsis_section
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    AllEntitiesListRenderer, \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.utils.rendering.entity_documentation_rendering import sorted_entity_list
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionRendererNode, \
    LeafSectionRendererNode, SectionRendererNodeWithSubSections
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
from exactly_lib.type_system.value_type import ElementType
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import transform_list_to_table


def hierarchy_generator(header: str,
                        all_type_entity_docs: list,
                        ) -> SectionHierarchyGenerator:
    """
    Utility to make a hierarchy from an `EntityConfiguration`
    """
    return HtmlDocHierarchyGeneratorForTypesHelp(header,
                                                 all_type_entity_docs)


class HtmlDocHierarchyGeneratorForTypesHelp(SectionHierarchyGenerator):
    def __init__(self,
                 header: str,
                 type_doc_list: list):
        """

        :param entity_2_section_contents_renderer: EntityDocumentation -> SectionContentsRenderer
        :param all_entities: [EntityDocumentation]
        """
        self.type_doc_list = type_doc_list
        self.header = header

    def section_renderer_node(self, target_factory: cross_ref.CustomTargetInfoFactory) -> SectionRendererNode:
        data_types = _types_of(ElementType.SYMBOL, self.type_doc_list)
        logic_types = _types_of(ElementType.LOGIC, self.type_doc_list)

        return SectionRendererNodeWithSubSections(
            target_factory.root(self.header),
            [],
            [
                self._type_category_node(_DATA_TYPES_HEADER, target_factory.sub_factory('data-type'), data_types),
                self._type_category_node(_LOGIC_TYPES_HEADER, target_factory.sub_factory('logic-type'), logic_types),
            ])

    def _type_category_node(self, header: str, target_factory: cross_ref.CustomTargetInfoFactory,
                            type_docs: list) -> SectionRendererNode:
        entity_nodes = [
            self._entity_node(entity)
            for entity in sorted_entity_list(type_docs)
        ]
        return SectionRendererNodeWithSubSections(target_factory.root(header),
                                                  [],
                                                  entity_nodes)

    @staticmethod
    def _entity_node(type_doc: TypeDocumentation) -> SectionRendererNode:
        target_info = cross_ref.TargetInfo(type_doc.singular_name(),
                                           type_doc.cross_reference_target())
        return LeafSectionRendererNode(target_info,
                                       IndividualTypeRenderer(type_doc))


class IndividualTypeRenderer(SectionContentsRenderer):
    def __init__(self, type_doc: TypeDocumentation):
        self.doc = type_doc
        self.rendering_environment = None
        format_map = {
            'act_phase': ACT_PHASE_NAME.emphasis,
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [docs.para(self.doc.single_line_description())]
        sub_sections = []

        if self.doc.invokation_variants():
            sub_sections.append(synopsis_section(
                invokation_variants_content(None,
                                            self.doc.invokation_variants(),
                                            [])))

        return doc.SectionContents(initial_paragraphs, sub_sections)


class TypesListRenderer(AllEntitiesListRenderer):
    def __init__(self, type_doc_list: list):
        super().__init__(single_line_description_as_summary_paragraphs, type_doc_list)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        data_types = _types_of(ElementType.SYMBOL, self.all_entities)
        logic_types = _types_of(ElementType.LOGIC, self.all_entities)
        return doc.SectionContents([],
                                   [
                                       self._section_for(_DATA_TYPES_HEADER, data_types),
                                       self._section_for(_LOGIC_TYPES_HEADER, logic_types),
                                   ])

    def _section_for(self, header: str, entities: list) -> doc.Section:
        return doc.Section(docs.text(header),
                           doc.SectionContents([transform_list_to_table(self._sorted_entities_list(entities))]))


def _types_of(element_type: ElementType, type_doc_list: list) -> list:
    return list(filter(lambda type_doc: type_doc.element_type is element_type,
                       type_doc_list))


_DATA_TYPES_HEADER = 'Data types'
_LOGIC_TYPES_HEADER = 'Logic types'
