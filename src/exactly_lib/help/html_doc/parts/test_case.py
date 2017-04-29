from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
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
from exactly_lib.util.textformat.structure import document as doc


class HtmlDocGeneratorForTestCaseHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 test_case_help: TestCaseHelp):
        super().__init__(rendering_environment, test_case_help.phase_helps_in_order_of_execution)
        self.test_case_help = test_case_help

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        specification_generator = test_case_specification_rendering.generator(
            'Specification of test case functionality',
            self.test_case_help)
        specification_node = specification_generator.section_renderer_node(targets_factory.sub_factory('spec'))

        cli_syntax_generator = cli_syntax.generator('Command line syntax')
        cli_syntax_node = cli_syntax_generator.section_renderer_node(targets_factory.sub_factory('cli-syntax'))

        phases_generator = self.generator_for_sections('Phases')
        phases_node = phases_generator.section_renderer_node(targets_factory.sub_factory('phases'))

        actors_targets_factory = cross_ref.sub_component_factory('actors', targets_factory)
        actors_target = actors_targets_factory.root('Actors')
        actors_sub_targets, actors_contents = self._actors_contents(actors_targets_factory)

        instructions_generator = self.generator_for_instructions_per_section('Instructions per phase')
        instructions_node = instructions_generator.section_renderer_node(targets_factory.sub_factory('instructions'))

        ret_val_contents = doc.SectionContents(
            [],
            [
                specification_node.section(self.rendering_environment),
                phases_node.section(self.rendering_environment),
                doc.Section(actors_target.anchor_text(),
                            actors_contents),
                cli_syntax_node.section(self.rendering_environment),
                instructions_node.section(self.rendering_environment),
            ]
        )
        ret_val_targets = [
            specification_node.target_info_node(),
            phases_node.target_info_node(),
            cross_ref.TargetInfoNode(actors_target,
                                     actors_sub_targets),
            cli_syntax_node.target_info_node(),
            instructions_node.target_info_node(),
        ]
        return ret_val_targets, ret_val_contents

    def _actors_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = HtmlDocGeneratorForEntitiesHelp(IndividualActorRenderer, ALL_ACTOR_DOCS, self.rendering_environment)
        return generator.apply(targets_factory)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestCasePhaseInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
