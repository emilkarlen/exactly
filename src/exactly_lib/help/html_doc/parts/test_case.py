from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
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
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.section_hierarchy_rendering import SectionGenerator
from exactly_lib.util.textformat.structure import document as doc


class HtmlDocGeneratorForTestCaseHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 test_case_help: TestCaseHelp,
                 rendering_environment: RenderingEnvironment):
        super().__init__(test_case_help.phase_helps_in_order_of_execution,
                         rendering_environment)
        self.test_case_help = test_case_help

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        specification_generator = test_case_specification_rendering.generator(
            'Specification of test case functionality',
            self.test_case_help)
        specification_node = specification_generator.section_renderer_node(targets_factory.sub_factory('spec'))

        cli_syntax_generator = cli_syntax.generator(texts.COMMAND_LINE_SYNTAX)
        cli_syntax_node = cli_syntax_generator.section_renderer_node(targets_factory.sub_factory('cli-syntax'))

        phases_generator = self.generator_for_sections('Phases')
        phases_node = phases_generator.section_renderer_node(targets_factory.sub_factory('phases'))

        actors_generator = self._actors_generator('Actors')
        actors_node = actors_generator.section_renderer_node(targets_factory.sub_factory('actors'))

        instructions_generator = self.generator_for_instructions_per_section('Instructions per phase')
        instructions_node = instructions_generator.section_renderer_node(targets_factory.sub_factory('instructions'))

        ret_val_contents = doc.SectionContents(
            [],
            [
                specification_node.section(self.rendering_environment),
                phases_node.section(self.rendering_environment),
                actors_node.section(self.rendering_environment),
                cli_syntax_node.section(self.rendering_environment),
                instructions_node.section(self.rendering_environment),
            ]
        )
        ret_val_targets = [
            specification_node.target_info_node(),
            phases_node.target_info_node(),
            actors_node.target_info_node(),
            cli_syntax_node.target_info_node(),
            instructions_node.target_info_node(),
        ]
        return ret_val_targets, ret_val_contents

    def _actors_generator(self, header: str) -> SectionGenerator:
        return HtmlDocGeneratorForEntitiesHelp(header, IndividualActorRenderer, ALL_ACTOR_DOCS)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
