from shellcheck_lib.help.concepts.concept_structure import ConceptDocumentation, ConceptDocumentationVisitor, \
    PlainConceptDocumentation, ConfigurationParameterDocumentation
from shellcheck_lib.help.concepts.utils import sorted_concepts_list
from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para, section


class AllConceptsListRenderer(SectionContentsRenderer):
    def __init__(self, concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help

    def apply(self) -> doc.SectionContents:
        return doc.SectionContents([sorted_concepts_list(self.concepts_help.all_concepts)], [])


class IndividualConceptRenderer(SectionContentsRenderer, ConceptDocumentationVisitor):
    def __init__(self, concept: ConceptDocumentation):
        self.concept = concept

    def apply(self) -> doc.SectionContents:
        return self.visit(self.concept)

    def visit_plain_concept(self, x: PlainConceptDocumentation) -> doc.SectionContents:
        purpose = x.purpose()
        initial_paragraphs = [para(purpose.single_line_description)]
        sub_sections = []
        if purpose.rest:
            sub_sections.append(self._rest_section(purpose))
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation) -> doc.SectionContents:
        purpose = x.purpose()
        initial_paragraphs = [para(purpose.single_line_description)]
        sub_sections = []
        sub_sections.append(section('Default Value',
                                    [x.default_value_para()]))
        if purpose.rest:
            sub_sections.append(self._rest_section(purpose))
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _rest_section(self, purpose):
        return section('Description',
                       purpose.rest)
