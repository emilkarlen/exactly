from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_case.contents.main import specification as test_case_specification_rendering
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_case.render.phase_documentation import TestCasePhaseDocumentationConstructor
from exactly_lib.help_texts.cross_ref import concrete_cross_refs as cross_ref
from exactly_lib.help_texts.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.help_texts.test_case.phase_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.util.textformat.construction.section_hierarchy import structures, hierarchy


def generator(header: str,
              test_case_help: TestCaseHelp) -> structures.SectionHierarchyGenerator:
    sections_helper = _HtmlDocGeneratorForTestCaseHelp(test_case_help)
    return hierarchy.parent(
        header,
        [],
        [
            ('spec',
             test_case_specification_rendering.generator(
                 'Specification of test case functionality',
                 test_case_help)
             ),
            ('phases',
             sections_helper.generator_for_sections('Phases')
             ),
            ('instructions',
             sections_helper.generator_for_instructions_per_section('Instructions per phase')
             ),
        ]
    )


class _HtmlDocGeneratorForTestCaseHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self, test_case_help: TestCaseHelp):
        super().__init__(SECTION_CONCEPT_NAME,
                         test_case_help.phase_helps_in_order_of_execution,
                         TestCasePhaseDocumentationConstructor)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
