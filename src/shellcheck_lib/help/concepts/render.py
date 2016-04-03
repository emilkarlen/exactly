from shellcheck_lib.help.concepts.concept import CONFIGURATION_PARAMETER_CONCEPT
from shellcheck_lib.help.concepts.concept_structure import ConceptDocumentation, ConceptDocumentationVisitor, \
    PlainConceptDocumentation, ConfigurationParameterDocumentation
from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib.help.utils.phase_names import phase_name_dictionary
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import para, section, text, SEPARATION_OF_HEADER_AND_CONTENTS, \
    paras


class AllConceptsListRenderer(SectionContentsRenderer):
    def __init__(self, concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help

    def apply(self) -> doc.SectionContents:
        return doc.SectionContents([_sorted_concepts_list(self.concepts_help.all_concepts)], [])


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


def _sorted_concepts_list(concepts: iter) -> ParagraphItem:
    all_cps = sorted(concepts, key=lambda cd: cd.name().singular)
    summary_constructor = _SummaryConstructor()
    items = [lists.HeaderContentListItem(text(cp.name().singular),
                                         summary_constructor.visit(cp))
             for cp in all_cps]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


class _SummaryConstructor(ConceptDocumentationVisitor):
    def visit_plain_concept(self, x: PlainConceptDocumentation):
        return x.summary_paragraphs()

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation):
        header = x.summary_paragraphs()
        footer = paras('This is a {cp} that can be set in the {phase[configuration]} phase.'
                       .format(cp=CONFIGURATION_PARAMETER_CONCEPT.name().singular,
                               phase=phase_name_dictionary()))
        return header + footer
