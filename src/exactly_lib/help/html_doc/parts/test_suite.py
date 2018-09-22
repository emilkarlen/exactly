from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.concrete_cross_refs import HelpPredefinedContentsPart, \
    PredefinedHelpContentsPartReference
from exactly_lib.definitions.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_suite.section_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.html_doc.parts.common.section_document_renderer import \
    GeneratorsForSectionDocument
from exactly_lib.help.program_modes.test_suite.contents.specification import main
from exactly_lib.help.program_modes.test_suite.contents.specification import structure as test_suite_structure
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.render.section_documentation import \
    TestSuiteSectionDocumentationConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator


def hierarchy(header: str,
              test_suite_help: TestSuiteHelp,
              suite_reporter_conf: EntityTypeConfiguration,
              ) -> generator.SectionHierarchyGenerator:
    sections_helper = GeneratorsForSectionDocument(SECTION_CONCEPT_NAME,
                                                   test_suite_help.section_helps,
                                                   TestSuiteSectionDocumentationConstructor)
    return h.hierarchy(
        header,
        children=[
            h.child('spec',
                    h.with_fixed_root_target(
                        PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_SUITE_SPEC),
                        main.hierarchy(misc_texts.TEST_SUITE_SPEC_TITLE,
                                       test_suite_help)
                    )),
            h.child('sections',
                    h.hierarchy(
                        'Sections',
                        children=[
                            h.child('cases-and-sub-suites',
                                    sections_helper.custom_sections_list(
                                        test_suite_structure.CASES_AND_SUB_SUITES_HEADER,
                                        test_suite_help.test_cases_and_sub_suites_sections,
                                    )),
                            h.child('common-case-contents',
                                    sections_helper.custom_sections_list(
                                        test_suite_structure.COMMON_CASE_CONTENTS_AND_CONFIG_HEADER,
                                        test_suite_help.test_case_phase_sections,
                                    )),
                        ])
                    ),
            h.child('reporters',
                    suite_reporter_conf.get_hierarchy_generator(
                        SUITE_REPORTER_ENTITY_TYPE_NAMES.name.plural.capitalize())
                    ),
            h.child('instructions',
                    sections_helper.instructions_per_section('Instructions per section')
                    ),
        ]
    )
