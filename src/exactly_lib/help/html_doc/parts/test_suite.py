from exactly_lib.definitions.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_suite.section_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.html_doc.parts.common.section_document_renderer import \
    HtmlDocGeneratorForSectionDocument
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
    sections_helper = HtmlDocGeneratorForSectionDocument(SECTION_CONCEPT_NAME,
                                                         test_suite_help.section_helps,
                                                         TestSuiteSectionDocumentationConstructor)
    return h.sections(
        header,
        [
            h.Node('spec',
                   SpecificationHierarchyGenerator('Specification of test suite functionality',
                                                   test_suite_help)
                   ),
            h.Node('sections',
                   h.sections(
                       'Sections',
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
