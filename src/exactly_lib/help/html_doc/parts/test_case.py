from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CrossReferenceId
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help import texts
from exactly_lib.help.actors.actor.all_actor_docs import ALL_ACTOR_DOCS
from exactly_lib.help.actors.render import IndividualActorRenderer
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import HtmlDocGeneratorForEntitiesHelp
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_case.contents import cli_syntax
from exactly_lib.help.program_modes.test_case.contents.main import specification as test_case_specification_rendering
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils import section_hierarchy_rendering
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment


def generator(header: str,
              test_case_help: TestCaseHelp,
              rendering_environment: RenderingEnvironment,
              ) -> section_hierarchy_rendering.SectionGenerator:
    sections_helper = _HtmlDocGeneratorForTestCaseHelp(test_case_help, rendering_environment)
    return section_hierarchy_rendering.parent(
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
            ('actors',
             HtmlDocGeneratorForEntitiesHelp('Actors',
                                             IndividualActorRenderer,
                                             ALL_ACTOR_DOCS)
             ),
            ('cli-syntax',
             cli_syntax.generator(texts.COMMAND_LINE_SYNTAX)
             ),
            ('instructions',
             sections_helper.generator_for_instructions_per_section('Instructions per phase')
             ),
        ]
    )


class _HtmlDocGeneratorForTestCaseHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 test_case_help: TestCaseHelp,
                 rendering_environment: RenderingEnvironment):
        super().__init__(test_case_help.phase_helps_in_order_of_execution,
                         rendering_environment)
        self.test_case_help = test_case_help

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
