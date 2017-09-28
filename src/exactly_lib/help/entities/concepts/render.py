import functools

from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation, ConceptDocumentationVisitor, \
    PlainConceptDocumentation, ConfigurationParameterDocumentation
from exactly_lib.help.entities.concepts.plain_concepts.configuration_parameter import CONFIGURATION_PARAMETER_CONCEPT
from exactly_lib.help.utils.rendering import parttioned_entity_set as pes
from exactly_lib.help.utils.rendering import see_also_section as render_utils
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help_texts.entity.concepts import CONFIGURATION_PARAMETER_CONCEPT_INFO
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para, section, paras


def _configuration_parameter_or_not(get_configuration_parameters: bool, type_doc_list: list) -> list:
    return list(filter(lambda concept_doc: concept_doc.is_configuration_parameter is get_configuration_parameters,
                       type_doc_list))


_PARTITIONS_SETUP = [
    pes.PartitionSetup(pes.PartitionNamesSetup('configuration-parameter-concept',
                                               CONFIGURATION_PARAMETER_CONCEPT_INFO.name.plural.capitalize()),
                       functools.partial(_configuration_parameter_or_not, True)
                       ),
    pes.PartitionSetup(pes.PartitionNamesSetup('other-concept',
                                               'Other concepts'),
                       functools.partial(_configuration_parameter_or_not, False)
                       ),
]


def hierarchy_generator_getter() -> pes.HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(_PARTITIONS_SETUP,
                                                   IndividualConceptRenderer)


def list_renderer_getter() -> pes.CliListRendererGetter:
    return pes.PartitionedCliListRendererGetter(
        _PARTITIONS_SETUP,
        lambda concept_doc: _SummaryConstructor().visit(concept_doc))


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
                       rest.sections)
        return [sect]

    def _see_also_sections(self) -> list:
        return render_utils.see_also_sections(self.concept.see_also_items(),
                                              self.rendering_environment)


class _SummaryConstructor(ConceptDocumentationVisitor):
    def visit_plain_concept(self, x: PlainConceptDocumentation) -> list:
        return x.summary_paragraphs()

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation) -> list:
        header = x.summary_paragraphs()
        footer = paras('This is a {cp} that can be set in the {phase[conf]} phase.'
                       .format(cp=formatting.concept(CONFIGURATION_PARAMETER_CONCEPT.name().singular),
                               phase=phase_name_dictionary()))
        return header + footer
