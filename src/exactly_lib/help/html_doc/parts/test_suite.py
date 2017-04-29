from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help import texts
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import HtmlDocGeneratorForEntitiesHelp
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents import cli_syntax
from exactly_lib.help.program_modes.test_suite.contents.specification import SpecificationRenderer
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.suite_reporters.render import IndividualSuiteReporterRenderer
from exactly_lib.help.suite_reporters.suite_reporter.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc


class HtmlDocGeneratorForTestSuiteHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 test_suite_help: TestSuiteHelp):
        super().__init__(rendering_environment, test_suite_help.section_helps)
        self.test_suite_help = test_suite_help

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        specification_targets_factory = cross_ref.sub_component_factory('spec', targets_factory)
        specification_target = specification_targets_factory.root('Specification of test suite functionality')
        specification_sub_targets, overview_contents = self._specification_contents(specification_targets_factory)

        cli_syntax_generator = cli_syntax.generator(texts.COMMAND_LINE_SYNTAX)
        cli_syntax_node = cli_syntax_generator.section_renderer_node(targets_factory.sub_factory('cli-syntax'))

        sections_generator = self.generator_for_sections('Sections')
        sections_node = sections_generator.section_renderer_node(targets_factory.sub_factory('sections'))

        reporters_targets_factory = cross_ref.sub_component_factory('reporters', targets_factory)
        reporters_target = reporters_targets_factory.root('Reporters')
        reporters_sub_targets, reporters_contents = self._reporters_contents(reporters_targets_factory)

        instructions_generator = self.generator_for_instructions_per_section('Instructions per section')
        instructions_node = instructions_generator.section_renderer_node(targets_factory.sub_factory('instructions'))

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(specification_target.anchor_text(),
                            overview_contents),
                sections_node.section(self.rendering_environment),
                doc.Section(reporters_target.anchor_text(),
                            reporters_contents),
                cli_syntax_node.section(self.rendering_environment),
                instructions_node.section(self.rendering_environment),
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(specification_target,
                                     specification_sub_targets),
            sections_node.target_info_node(),
            cross_ref.TargetInfoNode(reporters_target,
                                     reporters_sub_targets),
            cli_syntax_node.target_info_node(),
            instructions_node.target_info_node(),
        ]
        return ret_val_targets, ret_val_contents

    def _specification_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = SpecificationRenderer(self.test_suite_help, targets_factory)
        section_contents = generator.apply(self.rendering_environment)
        return generator.target_info_hierarchy(), section_contents

    def _reporters_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = HtmlDocGeneratorForEntitiesHelp('Reporters',
                                                    IndividualSuiteReporterRenderer,
                                                    ALL_SUITE_REPORTERS,
                                                    self.rendering_environment)
        return generator.apply(targets_factory)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
