from exactly_lib.definitions.test_case.phase_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.help.html_doc.parts.common.section_document_renderer import \
    GeneratorsForSectionDocument
from exactly_lib.help.program_modes.test_case.contents.specification import main as test_case_specification_rendering
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.help.program_modes.test_case.render.phase_documentation import TestCasePhaseDocumentationConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator


def hierarchy(header: str,
              test_case_help: TestCaseHelp) -> generator.SectionHierarchyGenerator:
    sections_helper = GeneratorsForSectionDocument(SECTION_CONCEPT_NAME,
                                                   test_case_help.phase_helps_in_order_of_execution,
                                                   TestCasePhaseDocumentationConstructor
                                                   )
    return h.sections(
        header,
        [
            h.Node('spec',
                   test_case_specification_rendering.root(
                       'Specification of test case functionality',
                       test_case_help)
                   ),
            h.Node('phases',
                   sections_helper.all_sections_list('Phases')
                   ),
            h.Node('instructions',
                   sections_helper.instructions_per_section('Instructions per phase')
                   ),
        ]
    )
