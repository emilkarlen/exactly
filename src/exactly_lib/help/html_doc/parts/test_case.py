from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
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
    return h.hierarchy(
        header,
        children=[
            h.child('spec',
                    h.with_fixed_root_target(
                        PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_SPEC),
                        test_case_specification_rendering.root(
                            misc_texts.TEST_CASE_SPEC_TITLE,
                            test_case_help))
                    ),
            h.child('phases',
                    sections_helper.all_sections_list('Phases')
                    ),
            h.child('instructions',
                    sections_helper.instructions_per_section('Instructions per phase')
                    ),
        ]
    )
