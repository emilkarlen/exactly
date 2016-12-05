from exactly_lib.help.concepts.contents_structure import ConceptDocumentation, ConceptDocumentationVisitor, \
    PlainConceptDocumentation, ConfigurationParameterDocumentation
from exactly_lib.help.concepts.plain_concepts.configuration_parameter import CONFIGURATION_PARAMETER_CONCEPT
from exactly_lib.help.utils.entity_documentation import AllEntitiesListRenderer
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.render import cross_reference_list
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para, section, paras


def all_concepts_list_renderer(all_concepts: list) -> SectionContentsRenderer:
    summary_constructor = _SummaryConstructor()
    return AllEntitiesListRenderer(summary_constructor.visit, all_concepts)


class IndividualConceptRenderer(SectionContentsRenderer, ConceptDocumentationVisitor):
    def __init__(self, concept: ConceptDocumentation):
        self.concept = concept
        self.rendering_environment = None

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        return self.visit(self.concept)

    def visit_plain_concept(self, x: PlainConceptDocumentation) -> doc.SectionContents:
        purpose = x.purpose()
        initial_paragraphs = [para(purpose.single_line_description)]
        sub_sections = []
        sub_sections.extend(self._rest_section(purpose))
        sub_sections.extend(self._see_also_sections())
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation) -> doc.SectionContents:
        purpose = x.purpose()
        initial_paragraphs = [para(purpose.single_line_description)]
        sub_sections = []
        sub_sections.append(section('Default Value',
                                    [x.default_value_para()]))
        sub_sections.extend(self._rest_section(purpose))
        sub_sections.extend(self._see_also_sections())
        return doc.SectionContents(initial_paragraphs, sub_sections)

    @staticmethod
    def _rest_section(purpose: DescriptionWithSubSections):
        rest = purpose.rest
        if rest.is_empty:
            return []
        sect = section('Description',
                       rest.initial_paragraphs,
                       sub_sections=rest.sections)
        return [sect]

    def _see_also_sections(self) -> list:
        if not self.concept.see_also():
            return []
        else:
            return [section('See also',
                            [cross_reference_list(self.concept.see_also(),
                                                  self.rendering_environment)])]


class _SummaryConstructor(ConceptDocumentationVisitor):
    def visit_plain_concept(self, x: PlainConceptDocumentation):
        return x.summary_paragraphs()

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation):
        header = x.summary_paragraphs()
        footer = paras('This is a {cp} that can be set in the {phase[conf]} phase.'
                       .format(cp=CONFIGURATION_PARAMETER_CONCEPT.name().singular,
                               phase=phase_name_dictionary()))
        return header + footer
