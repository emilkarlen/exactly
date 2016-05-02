from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.help.html_doc.parts.utils import HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.test_case.contents.main import overview as test_case_overview_rendering
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document  as doc


class HtmlDocGeneratorForTestCaseHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 test_case_help: TestCaseHelp):
        super().__init__(rendering_environment)
        self.test_case_help = test_case_help

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        overview_targets_factory = cross_ref.sub_component_factory('overview',
                                                                   targets_factory)
        overview_target = overview_targets_factory.root('Test Case Overview')
        overview_sub_targets, overview_contents = self._test_case_overview_contents(overview_targets_factory)

        phases_targets_factory = cross_ref.sub_component_factory('phases',
                                                                 targets_factory)
        phases_target = phases_targets_factory.root('Phases')
        phases_sub_targets, phases_contents = self._sections_contents(
            phases_targets_factory,
            self.test_case_help.phase_helps_in_order_of_execution)

        instructions_targets_factory = cross_ref.sub_component_factory('instructions',
                                                                       targets_factory)
        instructions_target = instructions_targets_factory.root('Instructions per phase')
        instructions_sub_targets, instructions_contents = self._instructions_contents(
            instructions_targets_factory,
            self.test_case_help.phase_helps_in_order_of_execution)

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(overview_target.anchor_text(),
                            overview_contents),
                doc.Section(phases_target.anchor_text(),
                            phases_contents),
                doc.Section(instructions_target.anchor_text(),
                            instructions_contents),
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(overview_target,
                                     overview_sub_targets),
            cross_ref.TargetInfoNode(phases_target,
                                     phases_sub_targets),
            cross_ref.TargetInfoNode(instructions_target,
                                     instructions_sub_targets),
        ]
        return ret_val_targets, ret_val_contents

    def _test_case_overview_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = test_case_overview_rendering.OverviewRenderer(self.test_case_help, targets_factory)
        section_contents = generator.apply(self.rendering_environment)
        return generator.target_info_hierarchy(), section_contents

    def _section_cross_ref_target(self, phase):
        return cross_ref.TestCasePhaseCrossReference(phase.name.plain)

    def _instruction_cross_ref_target(self, instruction_doc, section) -> CrossReferenceId:
        return cross_ref.TestCasePhaseInstructionCrossReference(
            section.name.plain,
            instruction_doc.instruction_name())
