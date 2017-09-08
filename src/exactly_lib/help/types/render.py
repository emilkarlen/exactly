from exactly_lib.help.html_doc.parts.utils import entities_list_renderer
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.types.contents_structure import TypeDocumentation
from exactly_lib.help.utils.doc_utils import synopsis_section
from exactly_lib.help.utils.rendering import section_hierarchy_rendering
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    AllEntitiesListRenderer, \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer, \
    SectionRendererFromSectionContentsRenderer, SectionRenderer, \
    section_contents_renderer_with_sub_sections
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
from exactly_lib.type_system.value_type import ElementType
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs

_DATA_TYPES_HEADER = 'Data types'
_LOGIC_TYPES_HEADER = 'Logic types'


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


def hierarchy_generator(header: str,
                        all_type_entity_docs: list,
                        ) -> section_hierarchy_rendering.SectionHierarchyGenerator:
    def section_generator(sub_header: str,
                          element_type: ElementType) -> section_hierarchy_rendering.SectionHierarchyGenerator:
        return entities_list_renderer.HtmlDocHierarchyGeneratorForEntitiesHelp(
            sub_header,
            IndividualTypeRenderer,
            _types_of(element_type,
                      all_type_entity_docs),
        )

    return section_hierarchy_rendering.parent(
        header,
        [],
        [
            (
                'data-type',
                section_generator(_DATA_TYPES_HEADER, ElementType.SYMBOL),
            ),
            (
                'logic-type',
                section_generator(_LOGIC_TYPES_HEADER, ElementType.LOGIC),
            ),
        ],

    )


def type_list_render(type_doc_list: list) -> SectionContentsRenderer:
    def section_renderer(header: str, element_type: ElementType) -> SectionRenderer:
        return SectionRendererFromSectionContentsRenderer(
            docs.text(header),
            AllEntitiesListRenderer(
                single_line_description_as_summary_paragraphs,
                _types_of(element_type, type_doc_list)))

    return section_contents_renderer_with_sub_sections([
        section_renderer(_DATA_TYPES_HEADER, ElementType.SYMBOL),
        section_renderer(_LOGIC_TYPES_HEADER, ElementType.LOGIC),
    ])


def _types_of(element_type: ElementType, type_doc_list: list) -> list:
    return list(filter(lambda type_doc: type_doc.element_type is element_type,
                       type_doc_list))
