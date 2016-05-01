from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.help.html_doc.parts.utils import HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.test_suite import render
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc


class HtmlDocGeneratorForTestSuiteHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 test_suite_help: TestSuiteHelp):
        super().__init__(rendering_environment)
        self.test_suite_help = test_suite_help

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        overview_targets_factory = cross_ref.sub_component_factory('overview',
                                                                   targets_factory)
        overview_target = overview_targets_factory.root('Test Suite Overview')
        overview_sub_targets, overview_contents = self._test_case_overview_contents(overview_targets_factory)

        phases_targets_factory = cross_ref.sub_component_factory('sections',
                                                                 targets_factory)
        phases_target = phases_targets_factory.root('Sections')
        phases_sub_targets, phases_contents = self._sections_contents(
            phases_targets_factory,
            self.test_suite_help.section_helps)

        instructions_targets_factory = cross_ref.sub_component_factory('instructions',
                                                                       targets_factory)
        instructions_target = instructions_targets_factory.root('Instructions')
        instructions_sub_targets, instructions_contents = self._instructions_contents(
            instructions_targets_factory,
            self.test_suite_help.section_helps)

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
        generator = render.OverviewRenderer(self.test_suite_help)
        section_contents = generator.apply(self.rendering_environment)
        return [], section_contents

    def _section_cross_ref_target(self, phase):
        return cross_ref.TestSuiteSectionCrossReference(phase.name.plain)

    def _instruction_cross_ref_target(self, instruction_doc, section) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionInstructionCrossReference(
            section.name.plain,
            instruction_doc.instruction_name())
