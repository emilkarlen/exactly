from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.actors.actor.all_actor_docs import ALL_ACTOR_DOCS
from exactly_lib.help.actors.render import IndividualActorRenderer
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import HtmlDocGeneratorForEntitiesHelp
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.test_case.contents.cli_syntax import TestCaseCliSyntaxDocumentation
from exactly_lib.help.program_modes.test_case.contents.main import specification as test_case_specification_rendering
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.cli_program_documentation_rendering import ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import document  as doc


class HtmlDocGeneratorForTestCaseHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 test_case_help: TestCaseHelp):
        super().__init__(rendering_environment)
        self.test_case_help = test_case_help

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        specification_targets_factory = cross_ref.sub_component_factory('spec',
                                                                        targets_factory)
        specification_target = specification_targets_factory.root('Specification of test case functionality')
        specification_sub_targets, specification_contents = self._specification_contents(
            specification_targets_factory)

        cli_syntax_targets_factory = cross_ref.sub_component_factory('cli-syntax',
                                                                     targets_factory)
        cli_syntax_target = cli_syntax_targets_factory.root('Command line syntax')
        cli_syntax_contents = self._cli_syntax_contents()

        phases_targets_factory = cross_ref.sub_component_factory('phases',
                                                                 targets_factory)
        phases_target = phases_targets_factory.root('Phases')
        phases_sub_targets, phases_contents = self._sections_contents(
            phases_targets_factory,
            self.test_case_help.phase_helps_in_order_of_execution)

        actors_targets_factory = cross_ref.sub_component_factory('actors', targets_factory)
        actors_target = actors_targets_factory.root('Actors')
        actors_sub_targets, actors_contents = self._actors_contents(actors_targets_factory)

        instructions_targets_factory = cross_ref.sub_component_factory('instructions',
                                                                       targets_factory)
        instructions_target = instructions_targets_factory.root('Instructions per phase')
        instructions_sub_targets, instructions_contents = self._instructions_contents(
            instructions_targets_factory,
            self.test_case_help.phase_helps_in_order_of_execution)

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(specification_target.anchor_text(),
                            specification_contents),
                doc.Section(phases_target.anchor_text(),
                            phases_contents),
                doc.Section(actors_target.anchor_text(),
                            actors_contents),
                doc.Section(cli_syntax_target.anchor_text(),
                            cli_syntax_contents),
                doc.Section(instructions_target.anchor_text(),
                            instructions_contents),
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(specification_target,
                                     specification_sub_targets),
            cross_ref.TargetInfoNode(phases_target,
                                     phases_sub_targets),
            cross_ref.TargetInfoNode(actors_target,
                                     actors_sub_targets),
            cross_ref.TargetInfoNode(cli_syntax_target, []),
            cross_ref.TargetInfoNode(instructions_target,
                                     instructions_sub_targets),
        ]
        return ret_val_targets, ret_val_contents

    def _specification_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = test_case_specification_rendering.SpecificationRenderer(self.test_case_help, targets_factory)
        section_contents = generator.apply(self.rendering_environment)
        return generator.target_info_hierarchy(), section_contents

    def _actors_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = HtmlDocGeneratorForEntitiesHelp(IndividualActorRenderer, ALL_ACTOR_DOCS, self.rendering_environment)
        return generator.apply(targets_factory)

    def _cli_syntax_contents(self) -> doc.SectionContents:
        renderer = ProgramDocumentationSectionContentsRenderer(TestCaseCliSyntaxDocumentation())
        return renderer.apply(self.rendering_environment)

    def _section_cross_ref_target(self, phase):
        return cross_ref.TestCasePhaseCrossReference(phase.name.plain)

    def _instruction_cross_ref_target(self, instruction_doc, section) -> CrossReferenceId:
        return cross_ref.TestCasePhaseInstructionCrossReference(
            section.name.plain,
            instruction_doc.instruction_name())
