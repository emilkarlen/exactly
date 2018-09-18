from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.definitions.cross_ref import concrete_cross_refs as cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_suite.section_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents.specification import structure as test_suite_structure
from exactly_lib.help.program_modes.test_suite.contents.specification.main import SpecificationHierarchyGenerator
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.render.section_documentation import \
    TestSuiteSectionDocumentationConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator


def hierarchy(header: str,
              test_suite_help: TestSuiteHelp,
              suite_reporter_conf: EntityTypeConfiguration,
              ) -> generator.SectionHierarchyGenerator:
    sections_helper = _HtmlDocGeneratorForTestSuiteHelp(test_suite_help)
    return h.parent(
        header,
        [],
        [
            h.Node('spec',
                   SpecificationHierarchyGenerator('Specification of test suite functionality',
                                                   test_suite_help)
                   ),
            h.Node('sections',
                   h.parent(
                       'Sections',
                       [],
                       [
                           h.Node('cases-and-sub-suites',
                                  sections_helper.generator_for_custom_sections(
                                      test_suite_structure.CASES_AND_SUB_SUITES_HEADER,
                                      test_suite_help.test_cases_and_sub_suites_sections,
                                  )),
                           h.Node('common-case-contents',
                                  sections_helper.generator_for_custom_sections(
                                      test_suite_structure.COMMON_CASE_CONTENTS_AND_CONFIG_HEADER,
                                      test_suite_help.test_case_phase_sections,
                                  )),
                       ])
                   ),
            h.Node('reporters',
                   suite_reporter_conf.get_hierarchy_generator(
                       SUITE_REPORTER_ENTITY_TYPE_NAMES.name.plural.capitalize())
                   ),
            h.Node('instructions',
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
