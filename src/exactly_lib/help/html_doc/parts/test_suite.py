from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents.specification import SpecificationHierarchyGenerator
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.section.render import TestSuiteSectionDocumentationConstructor
from exactly_lib.help_texts.cross_ref import concrete_cross_refs as cross_ref
from exactly_lib.help_texts.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.help_texts.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.help_texts.test_suite.section_names import SECTION_CONCEPT_NAME
from exactly_lib.util.textformat.construction.section_hierarchy import structures, hierarchy


def generator(header: str,
              test_suite_help: TestSuiteHelp,
              suite_reporter_conf: EntityTypeConfiguration,
              ) -> structures.SectionHierarchyGenerator:
    sections_helper = _HtmlDocGeneratorForTestSuiteHelp(test_suite_help)
    return hierarchy.parent(
        header,
        [],
        [
            ('spec',
             SpecificationHierarchyGenerator('Specification of test suite functionality',
                                             test_suite_help)
             ),
            ('sections',
             sections_helper.generator_for_sections('Sections')
             ),
            ('reporters',
             suite_reporter_conf.get_hierarchy_generator(SUITE_REPORTER_ENTITY_TYPE_NAMES.name.plural.capitalize())
             ),
            ('instructions',
             sections_helper.generator_for_instructions_per_section('Instructions per section')
             ),
        ]
    )


class _HtmlDocGeneratorForTestSuiteHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self, test_suite_help: TestSuiteHelp):
        super().__init__(SECTION_CONCEPT_NAME,
                         test_suite_help.section_helps,
                         TestSuiteSectionDocumentationConstructor)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
